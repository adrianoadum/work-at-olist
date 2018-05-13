# Work at Olist - Test Implementation

This is a test resolution for a job application at [Olist](https://olist.com/) as Python Web Developer.

The project is an API responsible for:
- Register phone call records
- Geneate monthly bill

## Deployed instance
The project was deployed on Heroku.
- Application: https://sheltered-stream-75763.herokuapp.com/
- API Documentation: https://sheltered-stream-75763.herokuapp.com/docs/

## Instructions
To make project work, follow the steps:
1. Clone or download the repo.
2. Install dependencies from requirements.txt
3. Create a PostgreSQL database and user, then configure settings.py
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Run:
   ```
   python manage.py runserver
   ```

Tests can be executed using the Django built-in test tool:
```
python manage.py test
```

## Used environment

The following environment was used to develop the project:
- Desktop: i7 7700k, 16GB DDR4, GTX1070 SLI, 490GB SSD, 2.3TB HDD
- Windows 10 Pro x64
- PostgreSQL 10 x64
- Visual Studio Code
- Python 3.6.5
- Django 2.0.5
- Django Rest Framework 3.8.2
