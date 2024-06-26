# Airport service API

## Description
API service for airport management written on DRF

## Features
- JWT authenticated
- Admin panel /admin/
- Documentation /api/doc/swagger/ and /api/doc/redoc/
- Creating airports, airplanes and routes
- Creating flights with crew
- Adding cities and airplane types
- Managing orders and tickets
- Filtering airports and flight

## Installing using GitHub
Duplicate .env.sample file as .env in the root of the project and update the environment variables

Install PostgresSQL and create db
```
cd path/to/your/directory

git clone https://github.com/aleksandra-prognimak/airport-api-service.git

python -m venv venv
```
   - Unix/Linux/macOS:
   ```
   source venv/bin/activate
   ```
   - Windows:
   ```
   .\venv\Scripts\activate
   ```
```
pip install requirements.txt

set POSTGRES_HOST=<your db hostname>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=<your db user password>
set DJANGO_SECRET_KEY=<your secret key>

python manage.py migrate

pythom manage.py runserver
```

## Run with docker
Docker should be installed

```
docker-compose build

docker-compose up
```

## Getting access
- Create user: /api/user/register/
- Get access token: /api/user/token/

![diagram.png](diagram.png)
