# Project recipe-api-app

A project for creating a Rest API for culinary recipes, including recipe pictures.

- Python + DJango + Django REST Framework;
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
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \ 
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
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
      - "8021:8000"
    volumes:
      - ./app:/app
    command: >
      sh -c "python manage.py runserver 0.0.0.0:8000"
    environment:
      - DB_HOST=db
      - DB_NAME=devdb
      - DB_USER=devuser
      - DB_PASS=devpass#1
    depends_on:
      - db

  db:
    image: postgres:13-alpine
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=devdb
      - POSTGRES_USER=devuser
      - POSTGRES_PASSWORD=devpass#1

volumes:
  dev-db-data:
  dev--data:

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

### Validate actions by Pushing the project

`$ git add .`

`$ git commit -am "First commit: added GitHub Actions."`

`$ git push origin`

See the Git Hub Actions running on the Actions section in the GitHub project.

## Test Driven Development

Create the tests first, and run it.

tests.py
```
"""
Samble tests
"""
from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):
    """Test the calc module."""

    def test_add_numbers(self):
        """Test adding numbers together."""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        """Test subtracting numbers."""
        res = calc.subtract(10,15)

        self.assertEqual(res, 5)
```

`$ docker-compose run --rm app sh -c "python manage.py test"`

Create methods matching the tests' expected results, and run it again.

calc.py
```
"""
Calculator functions
"""


def add(x, y):
    """Add x and y and return result."""
    return x + y

def subtract(x, y):
    """Subtract x from y and return result"""
    return y - x
```
`$ docker-compose run --rm app sh -c "python manage.py test"`

Result:
```
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

## Settings for PostgreSQL database

settings.py
```
(...)
import os
(...)
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}
(...)
```

## Fixing database race condition

It occours when the database service has started but the PostgreSQL engine is not started yet, and the application tries to connectgetting back an error.

### 1. Create new app: core

`$ docker-compose run --rm app sh -c "python manage.py startapp core"`

Delete files in the core directory:

- tests.py
- views.py

### 2. Setup settings

settings.py
```
(...)
INSTALLED_APPS = [
    (...)
    'core',
]
(...)
```

### 3. Create file structure into the core directory:

Files and directories into the core project

```
/core
- /management
  - __init__.py
  - /commands
    - __init__.py
    - wait_for_db.py
- /tests
  - __init__.py
  - test_commands.py
```

wait_for_db.py
```
"""Django command to wait for the database to be available."""

import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable. Waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database avallable!'))

```

test_commands.py
```
"""
Test custom Django management commands.
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test wait for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test wait for database when getting PperationalError."""
        patched_check.side_effect = [Psycopg2OpError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])

```

### 4. Run tests to provoke assertion errors

Run the mock test for the running condition:

`$ docker-compose run --rm app sh -c "python manage.py test"`

Test the real running condition fix, as well as the unit tests:

`$ docker-compose run --rm app sh -c "python manage.py wait_for_db && flake8"`