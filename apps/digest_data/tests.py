from django.test import TestCase, Client
from django.urls import reverse
from apps.digest_data.models import Law, TextChunk
from apps.user_authentication.models import User
import uuid

class LawModelTest(TestCase):
    def setUp(self):
        self.law_id = str(uuid.uuid4())
        self.law = Law.objects.create(
            id=self.law_id,
            metadata={"title": "Test Law", "category": "Civil"},
            filename="test_law.html"
        )

    def test_law_creation(self):
        """Test that a law can be created successfully."""
        self.assertEqual(self.law.id, self.law_id)
        self.assertEqual(self.law.metadata["title"], "Test Law")
        self.assertFalse(self.law.proccessed)

    def test_text_chunk_creation(self):
        """Test that text chunks can be created and linked to a law."""
        chunk = TextChunk.objects.create(
            fragment_number=1,
            content="This is a test chunk content.",
            law=self.law
        )
        self.assertEqual(chunk.law, self.law)
        self.assertEqual(self.law.chunks.count(), 1)

class DigestDataViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@example.com", password="password")
        # Law doesn't strictly require login based on DigestDataCrud, 
        # but the project seems to use authentication.
        self.law = Law.objects.create(
            id=str(uuid.uuid4()),
            metadata={"title": "Initial Law"},
            filename="initial.html"
        )
        self.url = reverse('laws-section')

    def test_digest_data_list_view(self):
        """Test that the law list view returns 200."""
        self.client.login(email="test@example.com", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "initial.html")

    def test_law_deletion(self):
        """Test that a law can be deleted via the view."""
        delete_url = reverse('delete-law', kwargs={'pk': self.law.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Law.objects.filter(id=self.law.id).exists())

    def test_law_creation_view(self):
        """Test that a law can be created via POST."""
        url = reverse('upsert-law')
        data = {
            'metadata': '{"title": "New Law"}', # View parses it as JSON if it was POSTed correctly
            'search': ''
        }
        # Note: handle_uploaded_file is called, might need mocking or a real small file
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile("new_law.html", b"<html>content</html>", content_type="text/html")
        
        response = self.client.post(url, {**data, 'file': test_file})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Law.objects.filter(filename="new_law.html").exists())
