# Le Recipes
## Tasty AI-generated recipes for you!

### How to use
1. Clone the repository
2. Install Python 3 and PIP
3. Create a virtual environment with `python -m venv venv`
4. Activate the virtual environment with `source venv/bin/activate`
5. Install the required packages with `pip install -r requirements.txt`
6. Install redis on the default port
7. Add .env file with a valid OPENAI_API_KEY
8. Start the Celery service `celery -A lerecipes worker -l info`
9. Start the Django server `python manage.py runserver`