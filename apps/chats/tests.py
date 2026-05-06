from django.test import TestCase, Client
from django.urls import reverse
from apps.user_authentication.models import User
from apps.chats.models import Conversation, Message
import uuid

class ChatModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="chat@example.com", password="password")
        self.conversation = Conversation.objects.create(
            slug=uuid.uuid4().hex,
            user=self.user,
            title="Test Conversation"
        )

    def test_conversation_creation(self):
        self.assertEqual(self.conversation.user, self.user)
        self.assertEqual(self.conversation.title, "Test Conversation")

    def test_message_creation(self):
        message = Message.objects.create(
            conversation=self.conversation,
            user_message="Hello Bot",
            bot_message="Hello User"
        )
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.user_message, "Hello Bot")

class ChatViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="view@example.com", password="password")
        self.client.login(email="view@example.com", password="password")
        self.conversation = Conversation.objects.create(
            slug=uuid.uuid4().hex,
            user=self.user,
            title="View Test"
        )
        self.chat_url = reverse('chats:chat-section')

    def test_chats_view_authenticated(self):
        """Test that the main chat view is accessible when logged in."""
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 200)

    def test_chats_view_unauthenticated(self):
        """Test that the chat view redirects when not logged in."""
        self.client.logout()
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_conversation_list_view(self):
        """Test that the message list for a conversation works."""
        url = reverse('chats:conversation', kwargs={'slug': self.conversation.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_conversation_delete(self):
        """Test that a conversation can be deleted."""
        url = reverse('chats:conversation-delete', kwargs={'slug': self.conversation.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Conversation.objects.filter(slug=self.conversation.slug).exists())

    def test_conversation_edit_title(self):
        """Test that a conversation title can be updated."""
        url = reverse('chats:conversation-edit-title', kwargs={'slug': self.conversation.slug})
        response = self.client.post(url, {'title': 'Updated Title'})
        self.assertEqual(response.status_code, 302) # Redirects after update
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.title, 'Updated Title')
