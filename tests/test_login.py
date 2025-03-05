import unittest
from app import create_app
from models import db, User

import unittest
from app import create_app
from models import db, User

class TestRegisterRoute(unittest.TestCase):
    def setUp(self):
        # Create an instance of the Flask app for testing
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

        # Initialize the database
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        # Test a successful registration
        response = self.client.post('/register', data={
            'user_firstname': 'John',
            'user_lastname': 'Doe',
            'user_email': 'johndoe@example.com',
            'user_password': 'securepassword123',
            'user_phone': '+1234567890'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Inscription réussie", response.data)

        with self.app.app_context():
            user = User.query.filter_by(user_email='johndoe@example.com').first()
            self.assertIsNotNone(user)

    def test_register_invalid_email(self):
        # Test with an invalid email
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'invalid-email',
            'user_password': 'securepassword123',
            'user_phone': '+1234567890'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Veuillez entrer une adresse email valide", response.data)

    def test_register_short_password(self):
        # Test with a short password
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'janedoe@example.com',
            'user_password': 'short',
            'user_phone': '+1234567890'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Le mot de passe doit contenir au moins 12 caractères.", response.data)

    def test_register_duplicate_email(self):
        # Test registration with an existing email
        with self.app.app_context():
            db.session.add(User(
                user_firstname="John",
                user_lastname="Doe",
                user_email="johndoe@example.com",
                user_password="securepassword123",
                user_phone="+1234567890"
            ))
            db.session.commit()

        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'johndoe@example.com',
            'user_password': 'securepassword123',
            'user_phone': '+1234567890'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cet email est déjà utilisé.", response.data)

    def test_register_invalid_phone(self):
        # Test with an invalid phone number
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'janedoe@example.com',
            'user_password': 'securepassword123',
            'user_phone': 'invalid-phone'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Veuillez entrer un numéro de téléphone valide.", response.data)

    def test_register_missing_fields(self):
        # Test with missing required fields
        response = self.client.post('/register', data={
            'user_firstname': '',
            'user_lastname': '',
            'user_email': '',
            'user_password': '',
            'user_phone': ''
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Le prénom et le nom doivent contenir au moins 3 caractères.", response.data)

if __name__ == '__main__':
    unittest.main()
