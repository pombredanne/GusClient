from simple_salesforce import Salesforce
from GusSession import GusSession
import getpass

class Client:
    sf_session = None
    
    def __init__(self):
        session = GusSession()
        try:
            self.__create_session__(session.load_session_id())
        except Exception as e:
            print e
            user = self.__prompt__('GUS Username', session.load_user_name())
            passwd = getpass.getpass('Please enter your GUS password: ')
            token = self.__prompt__('Security Token', session.load_gus_token())
                
            self.__create_session__(session.login(user, passwd, token))
            
    def __prompt__(self, prompt, default):
        if default is not None:
            default_prompt = ' [' + default + ']'
        else:
            default_prompt = ''
            
        return raw_input('Please Enter your %s%s: ' % (prompt, default_prompt)) or default
            
    def __create_session__(self, session_id):
        self.sf_session = Salesforce(instance_url='https://gus.salesforce.com', session_id=session_id)
        self.sf_session.query("select Id from ADM_Work__c where Name='NOTHING'") #See if the token is good

class NoRecordException(Exception):
    """nothing"""
    pass
