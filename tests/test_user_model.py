import unittest
from app import create_app, db
from app.models import User, Role, Course, Survey, Question


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        print('')
        print('Setting up database with user roles...')
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        print('Database successfully set up with user roles.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def tearDown(self):
        print('')
        print('Destroying database')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print('Database successfully destroyed.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def test_password_setter(self):
        print('')
        print('Testing password setter...')
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)
        print('Password successfully set.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def test_no_password_getter(self):
        print('')
        print('Testing password getter...')
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password
        print('Password successfully get.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def test_password_verification(self):
        print('')
        print('Testing password verification...')
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
        print('Password successfully verified.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def test_password_salts_are_random(self):
        print('')
        print('Testing randomness of password salts...')
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)
        print('Password salts are random.')


class RoleModelTestCase(unittest.TestCase):
    def setUp(self):
        print('')
        print('Setting up database with user roles...')
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        print('Database successfully set up with user roles.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def tearDown(self):
        print('')
        print('Destroying database...')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print('Database successfully destroyed.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def test_successfully_inserted(self):
        print('')
        print('Testing if user roles are successfully inserted...')
        self.assertTrue(len(Role.query.all()) == 4)
        print('User roles have been successfully inserted.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')


class ModelInsertionTestCase(unittest.TestCase):
    def setUp(self):
        print('')
        print('Setting up database with user roles...')
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        print('Database successfully set up with user roles.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def tearDown(self):
        print('')
        print('Destroying database...')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print('Database successfully destroyed.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def test_insert(self):
        print('')
        print('Creating an admin user...')
        role = Role.get_by_name('admin')
        self.assertTrue(role is not None)
        user = User(username='admin', role=role, password='cat')
        print('Admin user successfully created.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')
        print('Adding and committing an admin user into the database...')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(User.query.filter_by(
            username='admin').first() is not None)
        print('Admin user successfully added and committed into the database.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

        print('Creating a course...')
        c = Course(course_code='TEST')
        print('Course successfully created.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')
        print('Trying to add and commit course into database...')
        db.session.add(c)
        db.session.commit()
        self.assertTrue(Course.query.filter_by(
            course_code='TEST').first() is not None)
        print('Course successfully added and committed into database.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

        print('Creating a survey...')
        survey = Survey.create(description='blah test', times=['1', '2'],
                               owner_id=user.id, course=c.course_code)
        self.assertTrue(Survey.query.filter_by(
            description='blah test').first() is not None)
        print('Survey successfully created.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')
        print('Creating a question for the survey...')
        question = Question.create(
            description="a test question", owner_id=user.id, optional=False, q_type=1)
        self.assertTrue(question is not None)
        print('Question successfully created.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')
        print('Assigning question to survey...')
        survey.set_questions([question.id])
        self.assertTrue(survey.questions.all() is not None)
        print('Question successfully assigned.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')
        print('')
