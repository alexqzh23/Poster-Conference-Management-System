===========================

**########### Requirements**

Django==3.1.7\
IPy==1.01\
itsdangerous==2.0.1\
numpy==1.21.5

You can install these packages by following command,\
typing in the directory this read.me file is in:

`pip install -r requirements.txt`

**########### Start Django Server**

You can start by following command,

typing in the directory this read.me file is in:

`python manage.py runserver 8000`

**########### Project Directories**

├── **cms (django main app)**\
| ├── admin.py\
| ├── apps.py\
| ├── email\
| ├── forms.py\
| ├── migrations\
| ├── models.py\
| ├── models_committee.py\
| ├── models_conference.py\
| ├── models_luckdraw.py\
| ├── models_poster.py\
| ├── system_function.py\
| ├── templates\
| ├── tests.py\
| ├── urls.py\
| ├── views.py\
├── db.sqlite3 (##database)\
├── manage.py\
├── media/\
├── project\
| ├── settings.py\
| ├── urls.py\
| ├── wsgi.py\
├── readme.md\
├── requirements.txt\
└── static/
