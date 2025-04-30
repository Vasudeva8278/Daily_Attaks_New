# The Daily Attack - News Management Platform

A Django-based news management platform that enables content creation, AI enhancement, and multi-channel publishing with a focus on LinkedIn integration.

## Features

- Admin panel for news content management
- Role-based user authentication (admin, editor, publisher, analyst)
- Content workflow states (draft, review, published)
- Media management for images and videos
- Content categorization and tagging
- Rich text editor (WYSIWYG) for content creation
- Version history tracking
- Collaborative editing
- AI-powered content enhancement using Google's Gemini API
- LinkedIn publishing integration
- RESTful API for frontend integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/daily-attack.git
cd daily-attack
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
GEMINI_API_KEY=your-gemini-api-key
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## User Roles

- **Administrator**: Full access to all features
- **Editor**: Can create and edit articles
- **Publisher**: Can publish articles and manage LinkedIn integration
- **Analyst**: Can view analytics and reports

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 style guidelines. Use flake8 for linting:
```bash
flake8 .
```

## Deployment

1. Set up a production environment:
```bash
export DJANGO_SETTINGS_MODULE=daily_attack.settings.production
```

2. Collect static files:
```bash
python manage.py collectstatic
```

3. Run the production server:
```bash
gunicorn daily_attack.wsgi:application
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 