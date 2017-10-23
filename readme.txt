Section 1.  External python Libraries used:

alembic==0.8.10
bleach==1.4
blinker==1.3
click==6.7
colorama==0.2.7
coverage==3.7.1
dominate==2.3.1
Flask==0.12
Flask-Bootstrap==3.0.3.1
Flask-Cors==3.0.3
Flask-HTTPAuth==2.7.0
Flask-Login==0.3.1
Flask-Mail==0.9.0
Flask-Migrate==2.0.3
Flask-Moment==0.2.1
Flask-PageDown==0.1.4
Flask-Script==2.0.5
Flask-SQLAlchemy==2.1
Flask-WTF==0.14.2
ForgeryPy==0.1
graphviz==0.8
greenlet==0.4.12
html5lib==1.0b3
httpie==0.7.2
itsdangerous==0.24
Jinja2==2.9.5
Mako==1.0.6
Markdown==2.3.1
MarkupSafe==0.23
msgpack-python==0.4.8
neovim==0.1.13
Pygments==1.6
python-dateutil==2.6.1
python-editor==1.0.3
requests==2.1.0
selenium==2.45.0
six==1.4.1
SQLAlchemy==1.1.5
visitor==0.1.3
Werkzeug==0.11.15
WTForms==2.1


Section 2.

Firstly, you will need to activate the Python virtual environment and install all of the dependencies by entering "pip install -r requirement.txt" in the console while in the project’s root directory.

Secondly, you will need to setup the database by entering ”python manage.py reset" in the console while in the project’s root directory.

Thirdly, you will need to load the enrolments.csv passwords.csv and courses.csv into the database. The steps to do so are as follows:
You will first need to make sure all the required csv files are in the project’s root directory.
Then you have to enter "python manage.py load” in the console while in the project’s root directory. 
Please note that the loading will take awhile to complete.

Finally, you will be able to run the server by entering "python manage.py run" in the console while in the project’s root directory.
The server will now be running on http://127.0.0.1:9528/ or http://localhost:9528/

Section 3.

In order to run all of the test cases, you need to first unzip the test.zip file, and put all of the .py files into the tests directory.
Then, you can run the unit tests by entering "python manage.py test" in the console while in the project’s root directory

list of test cases:
test_404                                        (test_api.APITestCase)
test_bad_auth                                   (test_api.APITestCase)
test_no_auth                                    (test_api.APITestCase)
test_token_auth                                 (test_api.APITestCase)
test_unverified                                 (test_api.APITestCase)
test_app_exists                                 (test_basics.BasicTestCase)
test_app_is_testing                             (test_basics.BasicTestCase)
test_home_page                                  (test_client.FlaskClientTestCase)
test_core_database_functionality                (test_core.SystemTestCase)
test_core_api_functionality                     (test_core.SystemTestCase)
test_insert                                     (test_user_model.ModelInsertionTestCase)
test_successfully_inserted                      (test_user_model.RoleModelTestCase)
test_no_password_getter                         (test_user_model.UserModelTestCase)
test_password_salts_are_random                  (test_user_model.UserModelTestCase)
test_password_setter                            (test_user_model.UserModelTestCase)
test_password_verification                      (test_user_model.UserModelTestCase)
