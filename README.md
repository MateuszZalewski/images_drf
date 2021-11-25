# images_drf

## General info

Simple image hosting written in Django with expiring links functionality. (WORK IN PROGRESS)

## Technologies

* docker 20.10.8
* docker-compose 2.0.0
* python 3.9
* django 3.2.9
* django-rest-framework 3.12.4
* celery 5.2.1
* redis 4.0.2

## Quickstart

### Requirements

Docker and docker-compose are only requirements. The project was only tested on the docker and docker-compose versions
listed above.

### Setup

Clone the repository and run the following commands inside project directory.

```bash
docker-compose up --build
```

If you are running it for the first time run also.

```bash
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py loaddata tiers
```

After this, the app should be available at localhost:8000

## Usage

For now user creation is via /admin

## Structure

Endpoint | HTTP method | CRUD Method | Result
---------|-------------|-------------|-------
images | GET | READ | Get all images links
images | POST | CREATE | Add image
images/:pk | DELETE | DELETE | Remove image with pk specified
media/:path | GET | READ | Get image
media/:path/:height | GET | READ | Get image thumbnail
media/:path/expiring/:time | GET | CREATE | Create expiring link to access image
link/:name | GET | READ | Get image from expiring link