# final-year-project-dummy
**This is my final year  project**

Steps to execute:

Step1: clone the repository:<br />
        git clone git@github.com:komalkoutilya/final-year-project-dummy.git<br />
Step2: move to directory:<br />
        cd final-year-project-dummy<br />
step3: create virtual environment:<br />
        make sure you have python version 3.12.9<br />
        py -m venv .venv<br />
step4: Setup ExecutionPolicy:<br />
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser<br />
step5: Activate .venv:<br />
        .\.venv\Scripts\Activate.ps1<br />
Step6: Install requirements:<br />
        pip install -r requirements.txt<br />
Step7: Create Database:<br />
        cd app<br />
        py manage.py migrate<br />
Step8: Start Running app:<br />
        py manage.py runserver<br />
Step9: Open Browser and run app<br />
        **http://127.0.0.1:8000/**<br />
