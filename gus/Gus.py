from simple_salesforce import Salesforce
from GusSession import GusSession
import getpass, sys

class Client:
    '''
    Base class facilitates logging into GUS and setting up a session and
    not much else.  Use BacklogClient to work with tickets or implement
    your own based on simple_salesforce methods.
    '''
    sf_session = None
    sf_session_id = None
    
    def __init__(self, session_id=None):
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
                print "Seems we haven't logged you into GUS yet"
                sys.stdin = open('/dev/tty')
                user = self.__prompt__('GUS Username', session.load_user_name())
                passwd = getpass.getpass('Please enter your GUS password: ')
                token = self.__prompt__('Security Token', session.load_gus_token())
                    
                self.__create_session__(session.login(user, passwd, token))
                
    def get_user_id_for_email(self, email):
        try:
            result = self.sf_session.query("select Id from User where Email = '%s'" % email)
            userid = result['records'][0]['Id']
        except:
            userid = None
        
        return userid
    
    def get_current_user_id(self):
        session = GusSession()
        username = session.load_user_name()
        result = self.sf_session.query("select Id from User where Username='%s'" % username)
        return result['records'][0]['Id']
    
    def get_user_email(self, userid):
        result = self.sf_session.query("select Email from User where Id='%s'" % userid)
        return result['records'][0]['Email']
        
    def get_scrum_teams_for_user(self, userid):
        email = self.get_user_email(userid)
        result = self.sf_session.query("select Scrum_Team__c, Scrum_Team_Name__c from ADM_Scrum_Team_Member__c where Internal_Email__c = '%s'" % email)
        out = []
        for record in result['records']:
            out.append((record['Scrum_Team__c'], record['Scrum_Team_Name__c']))
            
        return out
            
    def __prompt__(self, prompt, default):
        if default is not None:
            default_prompt = ' [' + default + ']'
        else:
            default_prompt = ''
            
        return raw_input('Please Enter your %s%s: ' % (prompt, default_prompt)) or default
            
    def __create_session__(self, session_id):
        self.sf_session = Salesforce(instance_url='https://gus.salesforce.com', session_id=session_id)
        self.sf_session.query("select Id from ADM_Work__c where Name='NOTHING'") #See if the token is good
        self.sf_session_id = session_id
        
    def session_id(self):
        '''
        Returns the Gus Session ID
        '''
        return self.sf_session_id

class NoRecordException(Exception):
    """Thrown when record isn't found"""
    pass
