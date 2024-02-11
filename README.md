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

#### 5.1. Now I can build the empty project

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

### 4. Run tests

Run the mock test for the race condition:

`$ docker-compose run --rm app sh -c "python manage.py test"`

Test the real race condition fix, as well as the unit tests:

`$ docker-compose run --rm app sh -c "python manage.py wait_for_db && flake8"`


## ... Create User API and Other Configurations ...

...

## Build Recipe API

### 1. Recipe API Design

#### 1.1. Features

All features will be specific for the authenticated user:

- Create
- List
- View detail
- Update
- Delete

#### 1.2. Endpoints

- /recipes/
  - GET - List all recipes
  - POST - Create new recipe for the authenticated user
- /recipes/<recipe_id>/
  - GET - View details of recipe
  - PUT/PATCH - Update recipe
  - DELETE - Delete recipe

### 2. APIView vs Viewsets

#### What is a View?

- Handles the requests made to a particular URL.
- Django uses functions
- DRF (Django REST Frameword) uses classes
  - Reuse of code
  - Overide behavior
- DRF also support decorators
- **APIView** and **Viewsets** are Django base classes

#### APIView

- Focused around HTTP methods
- Class methods for API methods
  - GET, POST, PUT, PATCH, DELETE
- Provide flexibility over URLs and logic
- Useful for non CRUD APIs
  - Bespoke logic (eg: auth, jobs, external APIs)

#### Viewsets

- Focused around actions
  - Retrieve, delete, update, partial update, destroy
- Map to Django models
- Uses Routers to generate URLs
- Great for CRUD operations on models

### 3. Write tests for recipe model

**3.1. Create test**

app\core\tests\test_model_recipe.py
```
"""
Teste for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class RecipeModelTests(TestCase):
    """Tests for the Recipe model."""

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user (
            email='test@example.com',
            password='testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)

```

**3.2. Run the test (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 4. Create recipe model

**4.1. Write model**

- Recipes are linked to individual users.

app\core\models\recipe.py
```
"""
Recipe model.
"""
from django.conf import settings
from .user_manager import UserManager
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return self.title

```

**4.2. Enable model in the Django admin:**

- Add line at the end of the file
- There is no need for specifying a base class

> admin.site.register(models.Recipe)

**4.3. Create the migration**

`$ docker-compose run --rm app sh -c "python manage.py makemigrations"`

**4.4. Run the test again (success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 5. Create recipe app

**5.1. Create the app**

`$ docker-compose run --rm app sh -c "python manage.py startapp recipe"`

**5.2. Remove unnecessary files**

- /recipe/migrations/
- /recipe/admin.py
- /recipe/models.py
- /recipe/tests.py

**5.3. Create tests directory**

- /recipe/tests/
- /recipe/tests/__init__.py

**5.4. Add app to the list of installed apps**

app\app\settings.py

```
(...)

INSTALLED_APPS = [
  (...)
  'recipe',
]

(...)
```

### 6. Write tests for listing recipes

**6.1. app\recipe\tests\test_recipe_api.py**

```
"""
Tests for recipe API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    """Create and return the sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minnutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user= user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True) # many means a list, supressing it will returna single object
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'otherpass123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True) # many means a list, supressing it will returna single object
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

```

### 7. Implement recipe listing API

#### 7.1.Create serializers.py file

app\recipe\serializers.py
```
"""
Serializers for recipe API.
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

```

#### 7.2. Run tests (Fail)

`$ docker-compose run --rm app sh -c "python manage.py test"`

#### 7.3. Write views

app\recipe\views.py
```
"""
Views for the recipe API.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers



class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override the get queryset method
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

```

#### 7.4. Add urls

app\recipe\urls.py
```
"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]

```

#### 7.5. Add urls inside the main urls.py file

**Add to file**

app\app\urls.py
```
(...)
urlpatterns = [
  (...)
  path('api/recipe/', include('recipe.urls')),
]

```

**Run tests (Success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`


### 8. Write tests for recipes detail API

Edit file

app\recipe\tests\test_recipe_api.py
```
(...)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])

(...)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

```

**Run tests (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 9. Implement recipe detail API

The detail serializer is simply an extension of the recipe serializer.

app\recipe\serializers.py
```
(...)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields = ['description']


```

Modify RecipeViewSet class.

app\recipe\views.py
```
"""
Views for the recipe API.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers



class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override the get queryset method
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

```

**Run tests (Success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 10. Write tests for creating recipes

(...)

**Run tests (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 11. Implement create recipe API


