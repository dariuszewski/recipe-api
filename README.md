# Recipe API

## Commit History

### 01-getting-started
- project setup
- created custom user (model, forms and admin)
- added swagger

### 02-docker-and-postgres-config
- added dockerfiles (file, ignore and compose)
- defined services (api, db) and volumes
- run locally with `docker-compose up --build`

### 03-recipe-app 
- created recipe app with `docker-compose exec web python manage.py startapp recipe`
- added model testing
