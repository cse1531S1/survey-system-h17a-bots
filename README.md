# PROJECT



---



### Setup Instruction

1. install [python3](https://www.python.org/downloads/) an [pip3](https://pip.pypa.io/en/stable/installing/) on your machine

2. install virtualenv by `pip3 install virtualenv`

3. clone this repository and setup virtual environment

   ```shell
   // actually i prefer clone the repository with ssh keys
   $ git clone https://github.com/cse1531S1/survey-system-h17a-bots
   $ cd survey-system-h17a-bots
   ```

4. setup and activate the virtual environment

   ```shell
   (venv) $ virtualenv --python=python3 venv
   // activate the virtual environment
   (venv) $ source venv/bin/activate
   // after activation there would be a (venv) before the dollar sign like '(venv) $'
   ```

5. install project dependencies

   ```shell
   (venv) $ pip install -r requirement.txt
   ```

6. setup done, you could run the server now

   ```shell
   (venv) $ python manage.py runserver
   ```


