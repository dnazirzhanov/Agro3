# Agro3 Azure Deployment Guide

## 1. Environment Variables (.env)
Create a `.env` file in the project root with:
```
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-app-service-url,localhost
DATABASE_URL=postgres://<username>:<password>@<host>:5432/<dbname>
AZURE_ACCOUNT_NAME=your-blob-account-name
AZURE_ACCOUNT_KEY=your-blob-account-key
AZURE_MEDIA_CONTAINER=your-media-container
```

## 2. Install Required Packages
```
pip install dj-database-url whitenoise django-storages[azure]
```

## 3. Static & Media Files
- Static files are served via Whitenoise.
- Media files use Azure Blob Storage if environment variables are set.

## 4. Database
- Uses `DATABASE_URL` for Azure PostgreSQL.
- Local fallback is SQLite.

## 5. Azure App Service Setup
- Deploy code to Azure App Service.
- Set environment variables in Azure portal.
- Configure PostgreSQL and Blob Storage resources.

## 6. Collect Static Files
```
python manage.py collectstatic
```

## 7. Migrate Database
```
python manage.py migrate
```

## 8. Run Server
```
python manage.py runserver
```

## 9. Additional Notes
- Ensure all secrets and keys are stored securely.
- For production, set `DEBUG=False` and configure allowed hosts.
- For troubleshooting, check Azure App Service logs and Django error output.