# Project recipe-api-app

A project for creating a Rest API for culinary recipes, including recipe pictures.

- Python + DJango;
- PostgreSQL;
- Test Driven Design (TDD);
- GitHub Actions automation for code liting and unit tests;
- DockerHub + GitHub integeration;
- Automatic documentation with Swagger;

## System Setup

Install applications

- VS Code
- Docker Desktop
- Git

`$ docker --version`

`Docker version 24.0.7, build afdd53b`

`$ docker-compose --version`

`Docker Compose version v2.23.3-desktop.2`

`$ git version`

`git version 2.43.0.windows.1`

## Project Setup

### 1. On Docker Hub

Under Account Settings/Security, create an access Token for my Application. Prefferably the same nome of the app.

In the future, if I want to revoke access to the Docker Hub, I simply delete the Token.

### 2. On GitHub

Create repository for my Project:

- Create it Public;
- Mark to add README file;
- Mark to add .gitignore file;
- Clone the project on my Workspace;

`$ git clone git@github.com:valerio-oliveira/recipe-api-app.git`

Now, unthe the project's Settings/Secrets, add a new repository Secret:

- DOCKERHUB_USER : My DockerHub user name
- DOCKERHUB_TOKEN : The access Token I've created on step 1

### 3. Define Python Requirements

Open my project in VSCode

`/recipe-api-app/$ vscode .`

#### 3.1. requirements.txt

```
Django>=3.2.4,<3.3
djangorestframework>=3.12.4,<3.13
```

### 4. Dockerfile

```
FROM python:3.9-alpine3.13
LABEL maintainer="Valerio Oliveira - valerio.net@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \ 
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        vfoapp-user 

ENV PATH="/py/bin:$PATH"

USER vfoapp-user
```

### 5. .gitignore
```
# Git
.git
.gitignore

# Docker
.docker

# Python
app/__pycache__/
app/*/__pycache__/
app/*/*/__pycache__/
app/*/*/*/__pycache__/
.env/
.venv/
venv/
```

#### 5.1. Now I can build the empty propject

`$ docker-compose build`

### 6. docker-compose.yml

```
version: "3.9"

services:
  app:
    build:
      context: .
      args:
        - DEV=true
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    command: >
      sh -c "python manage.py runserver 0.0.0.0:8000"

```

### 7. Lint and Test : flake8

#### 7.1. requirements.dev.txt

```
flake8>=3.9.2,<3.10
```

#### 7.2. Validate building the empty propject

`$ docker-compose build`

### 8. .flake8

Under /app/ directory
```
[flake8]
exclude =
    migrations,
    __pycache__,
    manage.py,
    settings.py
```

#### 8.1. Run the Linting tool

`$ docker-compose run --rm app sh -c "flake8"`

### 9. Create Django project

`$ docker-compose run --rm app sh -c "django-admin startproject app ."`

#### 9.1. Now I can run the Django project

`$ docker-compose up`

## Configure GitHub Actions

/.github/workflows/checks.yml
```
---
name: Checks

on: [push]

jobs:
  test-lint:
    name: Test and Lint
    runs-on: ubuntu-20.04
    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Checkout
        uses: actions/checkout@v2
      - name: Test
        run: docker-compose run --rm app sh -c "python manage.py test"
      - name: Lint
        run: docker-compose run --rm app sh -c "flake8"
```

