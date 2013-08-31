from simple_salesforce import Salesforce
from GusSession import GusSession
from ui.Login import Factory
import sys

class Client:
    '''
    Base class facilitates logging into GUS and setting up a session and
    not much else.  Use BacklogClient to work with tickets or implement
    your own based on simple_salesforce methods.
    '''
    
    def __init__(self, session_id=None):
        self.sf_session = None
        self.sf_session_id = None

        if session_id is not None: #remote initialization
            try:
                self.__create_session__(session_id)
            except Exception as e:
                print "Unable to Create Session with passed token: %s" % session_id
                print e
        else: #local initialization
            session = GusSession()
            try:
                self.__create_session__(session.load_session_id())
            except Exception as e:
                if sys.stdin.isatty():
                    login = Factory().get_login('CLI', 'Looks like we need to login to Gus...')
                else:
                    login = Factory().get_login('GUI', 'Looks like we need to login to Gus...')
                    
                login.add_prompt('user', 'GUS UserName', 'TEXT', session.load_user_name())
                login.add_prompt('password', 'GUS Password', 'PASSWORD')
                login.add_prompt('token', 'GUS Security Token', 'TEXT', session.load_gus_token())

                counter = 0
                while self.sf_session_id is None and counter < 3:
                    login.display()
                    user = login.get_value('user')
                    passwd = login.get_value('password')
                    token = login.get_value('token')
                        
                    self.__create_session__(session.login(user, passwd, token))
                    
                if self.sf_session_id is None:
                    raise Exception('Not Logged into GUS')
                
    def __create_session__(self, session_id):
        '''
        Creates a simple_salesforce session and checks to see if it is valid
        '''
        self.sf_session = Salesforce(instance_url='https://gus.salesforce.com', session_id=session_id)
        self.sf_session.query("select Id from ADM_Work__c where Name='NOTHING'") #See if the token is good
        self.sf_session_id = session_id
        
    def session_id(self):
        '''
        Returns the Gus Session ID
        '''
        return self.sf_session_id

    def get_user_id_for_email(self, email):
        '''
        Determines the object id of a user by looking up the record with the user's email address
        '''
        try:
            result = self.sf_session.query("select Id from User where Email = '%s'" % email)
            userid = result['records'][0]['Id']
        except:
            userid = None
        
        return userid
    
    def get_current_user_id(self):
        '''
        Determines the ID of the currently logged in user
        '''
        session = GusSession()
        username = session.load_user_name()
        result = self.sf_session.query("select Id from User where Username='%s'" % username)
        return result['records'][0]['Id']
    
    def get_user_email(self, userid):
        '''
        Determines the email address of the specified user id
        '''
        result = self.sf_session.query("select Email from User where Id='%s'" % userid)
        return result['records'][0]['Email']
        
    def get_scrum_teams_for_user(self, userid):
        '''
        Returns a list of team id, team name tuples that the specified user is a member of with > 0% allocation
        '''
        email = self.get_user_email(userid)
        result = self.sf_session.query("select Scrum_Team__c, Scrum_Team_Name__c from ADM_Scrum_Team_Member__c where Internal_Email__c = '%s' and Allocation__c > 0" % email)
        out = []
        for record in result['records']:
            out.append((record['Scrum_Team__c'], record['Scrum_Team_Name__c']))
            
        return out
    
    def get_team_record(self, teamid):
        '''
        Returns the record for a specified team id
        '''
        team = self.sf_session.ADM_Scrum_Team__c.get(teamid)
        return team
    
    def get_dependency_record(self, dependency_id):
        '''
        Returns the record for the specified dependency record id
        '''
        result = self.sf_session.ADM_Team_Dependency__c.get(dependency_id)
        return result
    
    def find_work(self, work_name):
        '''
        Returns the work record for the work specified by name
        '''
        result = self.sf_session.query("select Id from ADM_Work__c where Name='%s'" % work_name)
        try:
            work_id = result["records"][0]["Id"]
            work = self.get_work_record(work_id)
        except:
            raise NoRecordException('Can\'t find work ' + work_name)

        return work

    def get_work_record(self, work_id):
        '''
        Returns the record for the specified work record id
        '''
        if work_id is not None:
            result = self.sf_session.ADM_Work__c.get(work_id)
        else:
            result = None
            
        return result
    
    def get_parent_work_for_work(self, workid):
        '''
        Returns a list of work record ids that are 'parents' to the specified work
        '''
        result = self.sf_session.query("Select Parent_Work__c from ADM_Parent_Work__c where Child_Work__c='%s'" % workid)
        return [x['Parent_Work__c'] for x in result['records']]
    
    def get_child_work_for_work(self, workid):
        '''
        Returns a list of work record ids that are 'children' to the specified work
        '''
        result = self.sf_session.query("Select Child_Work_c from ADM_Parent_Work__c where Parent_Work__c='%s'" % workid)
        return [x['Child_Work__c'] for x in result['records']]
    
    def get_sprint_for_work(self, workid):
        work = self.get_work_record(workid)
        if work['Sprint__c'] is not None:
            sprint = self.get_sprint_record(work['Sprint__c'])
        else:
            sprint = None
            
        return sprint
    
    def get_work_tree(self, workid):
        work = self.get_work_record(workid)
        work.parents = []
        parents = self.get_parent_work_for_work(workid)
        for parent in parents:
            work.parents.append(self.get_work_tree(parent))
            
        work.children = []
        children = self.get_child_work_for_work(workid)
        for child in children:
            work.children.append(self.get_work_tree(child))
            
        return work

    def get_build_record(self, build_id):
        '''
        Returns the build for the specified build record id
        '''
        result = self.sf_session.ADM_Build__c.get(build_id)
        return result
    
    def find_build_id(self, build_name):
        '''
        Returns the id for a build specified by name
        '''
        result = self.sf_session.query("select Id from ADM_Build__c where Name='%s'" % build_name)
        try:
            build_id = result["records"][0]["Id"]
        except:
            raise NoRecordException('Can\'t find build ' + build_name)

        return build_id

    def get_sprint_record(self, sprint_id):
        '''
        Returns the record for the specified sprint record id
        '''
        result = self.sf_session.ADM_Sprint__c.get(sprint_id)
        return result
    
    def get_current_sprint_for_team(self, teamid):
        '''
        Returns the Id of the current sprint for the specified team
        '''
        try:
            sprints = self.sf_session.query("select Id from ADM_Sprint__c where Scrum_Team__c = '%s' and Days_Remaining__c not in('CLOSED','NOT STARTED')" % teamid)
            sprint_id = sprints['records'][0]['Id']
        except:
            sprint_id = None
            
        return sprint_id
            
class NoRecordException(Exception):
    """Thrown when record isn't found"""
    pass
