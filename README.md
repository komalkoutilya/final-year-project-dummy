# final-year-project-dummy
**This is my final year  project**

Steps to execute:

Step1: clone the repository:
        git clone git@github.com:komalkoutilya/final-year-project-dummy.git
Step2: move to directory:
        cd final-year-project-dummy
step3: create virtual environment:
        make sure you have python version 3.12.9
        py -m venv .venv
step4: Setup ExecutionPolicy:
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
step5: Activate .venv:
        .\.venv\Scripts\Activate.ps1
Step6: Install requirements:
        pip install -r requirements.txt
Step7: Create Database:
        cd app
        py manage.py migrate
Step8: Start Running app:
        py manage.py runserver
Step9: Open Browser and run app
        **http://127.0.0.1:8000/**
