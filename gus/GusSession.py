import httplib, re
from userdata.Store import Store

class GusSession(Store):
    '''
    Persists and loads local session data to facilitate login to
    Gus specifically.
    '''
    
    def login(self, user, password, security_token):
        '''
        Authenticates to Gus using a Soap Login with a provided username, password and
        security token.  Returns the Gus Session ID
        '''
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
        
        self.store(session_id=sessionId, token=security_token, user_name=user)

        return sessionId
    
    def load_gus_token(self):
        '''
        Retrieves the locally cached security token or None if not found
        '''
        return self.__get_local__('token')
    
    def load_session_id(self):
        '''
        Retrieves the locally cached Gus Session ID or None if not found
        '''
        return self.__get_local__('session_id')
    
    def load_user_name(self):
        '''
        Retrieves the locally cached Gus username or None if not found
        '''
        return self.__get_local__('user_name')
    
