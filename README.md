# PROJECT


Before making your contribution please check our working progress [here](https://docs.google.com/document/d/1TzG5yQ7I7R_76ya9ORNKC6MaxUXVMQIUMHUQFK8QuIs/edit).


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


### FAQ

1. HOW COULD I INIT THE DATABASE?

```shell
// remember activate the virtual environment first
$ python manage.py shell
// then you will be in the intractive python shell
>> db.drop_all()
// press enter
>> db.create_all()
// WOOHOO! a brand new database is initialised
```

2. HOW DO I RUN THE FRONTEND??


```shell
$ cd frontend
$ npm install
$ npm run dev
// then after a while, the frontend will be available on localhost:9527
```
