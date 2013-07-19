import httplib, pickle, re, os
from os.path import expanduser

class GusSession:
    __local_file__ = ''
    
    def __init__(self, filename='.gus_data'):
        self.__local_file__ = expanduser("~") + '/' + filename

    def login(self, user, password, security_token):
        headers = {
        	'User-Agent'	  : 'gus-client',
        	'Accept'		  : 'text/html,application/xhtml+xml,application/xml',
        	'Accept-Encoding' : 'none',
        	'Accept-Charset'  : 'utf-8',
        	'Connection'	  : 'close',
        	'Content-Type'	: 'text/xml; charset=utf-8',
        	'SOAPAction'	  : '"urn:enterprise.soap.sforce.com/login"'}
        body = '''
        	<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="urn:enterprise.soap.sforce.com" xmlns:fns="urn:fault.enterprise.soap.sforce.com" xmlns:ens="urn:sobject.enterprise.soap.sforce.com"><soap:Header></soap:Header><soap:Body><tns:login><username>%s</username><password>%s%s</password></tns:login></soap:Body></soap:Envelope>
        		''' % (user, password, security_token)
        conn = httplib.HTTPSConnection('gus.salesforce.com')
        conn.request('POST', '/services/Soap/c/v27.0', body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        regex = re.compile("<sessionId>(.*)</sessionId>", re.MULTILINE)
        match = regex.search(data)
        sessionId = match.group(1)
        
        self.store(sessionid=sessionId, token=security_token, username=user)

        return sessionId
    
    def __load_data__(self):
        try:
            with open(self.__local_file__, 'r') as existing:
                gus_data = pickle.load(existing)
                existing.close()
        except:
            gus_data = {}
        
        return gus_data
        
    def __get_local__(self, attribute):
        try:
            gus_data = self.__load_data__()
            out = gus_data[attribute]
        except:
            out = None
            
        return out
        
    def load_gus_token(self):
        return self.__get_local__('token')
    
    def load_session_id(self):
        return self.__get_local__('session_id')
    
    def load_user_name(self):
        return self.__get_local__('user_name')
        
    def __store_data__(self, gus_data):
        with open(self.__local_file__, 'w') as f:
            pickle.dump(gus_data, f)
            f.close()

    def store(self, sessionid='', token='', username=''):
        gus_data = self.__load_data__()
        
        if sessionid != '':
            gus_data['session_id'] = sessionid
            
        if token != '':
            gus_data['token'] = token
            
        if username != '':
            gus_data['user_name'] = username
            
        self.__store_data__(gus_data)
        
    def remove_local(self):
        try:
            os.unlink(self.__local_file__);
        except:
            pass
        