import unittest
import json
from app import create_app

class ChatAPITestCase(unittest.TestCase):
    """Test case for the chat API."""
    
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = create_app('testing')
        self.client = self.app.test_client
        
        # Test message data
        self.message = {
            'sender': 'test_user',
            'content': 'Hello, this is a test message!'
        }
    
    def test_message_creation(self):
        """Test API can create a message (POST request)."""
        res = self.client().post('/api/messages',
                                data=json.dumps(self.message),
                                content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('Message created successfully', str(res.data))
    
    def test_get_all_messages(self):
        """Test API can get all messages (GET request)."""
        # First create a test message
        self.client().post('/api/messages',
                          data=json.dumps(self.message),
                          content_type='application/json')
        
        # Then get all messages
        res = self.client().get('/api/messages')
        self.assertEqual(res.status_code, 200)
        self.assertIn('success', str(res.data))
    
    def test_get_message_by_id(self):
        """Test API can get a single message by ID (GET request)."""
        # First create a test message
        post_res = self.client().post('/api/messages',
                                     data=json.dumps(self.message),
                                     content_type='application/json')
        post_data = json.loads(post_res.data)
        message_id = post_data['data']['id']
        
        # Then get the message by ID
        res = self.client().get(f'/api/messages/{message_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn('success', str(res.data))
    
    def test_delete_message(self):
        """Test API can delete a message (DELETE request)."""
        # First create a test message
        post_res = self.client().post('/api/messages',
                                     data=json.dumps(self.message),
                                     content_type='application/json')
        post_data = json.loads(post_res.data)
        message_id = post_data['data']['id']
        
        # Then delete the message
        res = self.client().delete(f'/api/messages/{message_id}')
        self.assertEqual(res.status_code, 200)
        
        # Try to get the deleted message
        res = self.client().get(f'/api/messages/{message_id}')
        self.assertEqual(res.status_code, 404)

if __name__ == '__main__':
    unittest.main()
