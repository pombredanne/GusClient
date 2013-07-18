from ..GusSession import GusSession
import unittest

class GusSessionTest(unittest.TestCase):
    session = None
    
    def setUp(self):
        self.session = GusSession(filename='.test_file')
        
    def tearDown(self):
        self.session.remove_local()
        
    def test_token_is_none_when_new_install(self):
        self.session.remove_local()
        token = self.session.load_gus_token()
        self.assertIsNone(token)
        
    def test_can_retrieve_stored_token(self):
        token = '123456'
        self.session.store(token=token)
        self.assertEqual(self.session.load_gus_token(), token, 'Couldn\'t get stored token')
        
    def test_can_retrieve_stored_session(self):
        sess = '1234556'
        self.session.store(sessionid=sess)
        self.assertEqual(self.session.load_session_id(), sess, 'Couldn\'t get stored session')
    