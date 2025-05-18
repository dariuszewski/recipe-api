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
- created recipe app with `docker-compose exec api python manage.py startapp recipe`
- added model testing

### 04-authentication
- added registration with email confirmation
- added jwt authentication
- used `djoser` and `djangorestframework-simplejwt`

### 05-authorization
- users can see only published recipes (list and detail)
- only authorized users can add recipes
- recipe is not published by default
- `DELETE` endpoint to only unpublishes recipes
- only owners can update/delete recipes
- users can see all their recipes in a separate endpoint
- changed the group name from api to recipe in swagger

### 06-token-blacklisting-and-expiration
- refresh token blaclisting
- extend experiation time of access token for development purposes

# TODO: recipe validation, testing, email service, images, pagination-searching-ordering, caching, rate limiting