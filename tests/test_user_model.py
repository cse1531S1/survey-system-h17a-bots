import unittest
from app import create_app, db
from app.models import User, Role, Course, Survey, Question, Answer, AnswerEntity


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)


class RoleModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successfully_inserted(self):
        self.assertTrue(len(Role.query.all()) == 4)


class ModelInsertionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_insert(self):
        role = Role.get_by_name('admin')
        self.assertTrue(role is not None)

        user = User(username='admin', role=role, password='cat')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(User.query.filter_by(
            username='admin').first() is not None)

        c = Course(course_code='TEST')
        db.session.add(c)
        db.session.commit()
        self.assertTrue(Course.query.filter_by(
            course_code='TEST').first() is not None)

        survey = Survey.create(description='blah test', owner_id=user.id)
