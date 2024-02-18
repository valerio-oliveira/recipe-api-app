# Project recipe-api-app

A project for creating a Rest API for culinary recipes, including recipe pictures.


## Overview


### API Features

- User authentication
- Creating objects
- Filtering and sorting objects
- Uploading and viewing images


### Technologies

- Python + DJango + Django REST Framework;
- PostgreSQL;
- GitHub Actions automation for code liting and unit tests;
- DockerHub + GitHub integeration;
- Swagger UI;


### Apps

- app/ - Django project
- app/core/ - Code shared between multiple apps
- app/user/ - User related code
- app/recipe/ - Recipe related code


### Test Driven Development (TDD)

- Is a development best practice
- Inverted approach: focus on how to test the code, not how to code
  - Start writing the test
  - Run the test so it should fail
  - Add the feature
  - Run the test again so it will pass
  - Refactor the code and test again


**Unit Tests**

- Code which tests code
  - Sets up conditions/inputs
  - Runs a piece of code
  - Checks output with "assertions"

- Benefits
  - Ensure code runs as expected
  - Catches bugs
  - Improves reliability
  - Provides confidence


## System Setup


### Applications to install

- VS Code
- Docker Desktop / Docker for Linux
- Git


### Verify instalation

`$ docker --version`

> Docker version 24.0.7, build afdd53b

`$ docker-compose --version`

> Docker Compose version v2.23.3-desktop.2`

`$ git version`

> git version 2.43.0.windows.1`


## Why use Docker?

- Consistent Dev and Prod environment
- Easier collaboration
- Capture all dependencies as code
  - Python requirements
  - Operating system dependencies
- Easier cleanup


## Project Setup


### 1. On Docker Hub

Under Account Settings/Security, create (and copy) the access Token for my Application. Preferably the same nome of the app.

In the future, if I want to revoke access to the Docker Hub, I can simply delete the Token.


### 2. On GitHub

**Create repository for my Project**

- Name: recipe-app-api
- Description: Recipe API project.
- Mark as Public;
- Mark to add README file;
- Mark to add .gitignore file;
  - In drop-down, select python template;


**Clone the project on my Workspace**

`$ git clone git@github.com:valerio-oliveira/recipe-api-app.git`

**Under the project's Settings/Secrets, add new repository Secrets**

> DOCKERHUB_USER : My DockerHub user name
> DOCKERHUB_TOKEN : The access Token I've created on step 1


### 3. Define Python Requirements

Open my project in VSCode

`/recipe-api-app/$ vscode .`


#### 3.1. requirements.txt

``` py
Django>=3.2.4,<3.3
djangorestframework>=3.12.4,<3.13
```

### 4. Dockerfile

``` Dockerfile
FROM python:3.9-alpine3.13
LABEL maintainer="valerio.net@gmail.com"

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

### 5. .dockerignore

``` py
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

#### 5.1. Building the empty project

`$ docker-compose build`

### 6. docker-compose.yml

``` yaml
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

Development dependencies will not be deployed with the production server.

``` py
flake8>=3.9.2,<3.10
```


#### 7.2. Validate building the empty propject

`$ docker-compose build`


### 8. .flake8

Under /app/ directory
``` ini
[flake8]
exclude =
    migrations,
    __pycache__,
    manage.py,
    settings.py
```


#### 8.1. Run the linting tests

`$ docker-compose run --rm app sh -c "flake8"`


### 9. Create Django project

`$ docker-compose run --rm app sh -c "django-admin startproject app ."`

> http://localhost:8021

#### 9.1. Run the Django project

`$ docker-compose up`


## Configure GitHub Actions


/.github/workflows/checks.yml
``` yaml
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


### Validate actions by pushing the project

`$ git add .`

`$ git commit -am "First commit: added GitHub Actions."`

`$ git push origin`

See the Git Hub Actions running on the Actions section in the GitHub project.


## Test Driven Development

*Create the tests first, and run it.*

Create methods matching the tests' expected results, and run it again.


### Test Classes

- SimpleTestCase
  - No database integration
  - Useful if no database is required
  - Save time executing tests, because doesn't have do clear database
- TestCase
  - Has database integration
  - Useful if testing code that uses database


### Writing tests

- Import test class
- Import objects to test
- Define test class, based on the corresponding base class
- Add test method nnamed with prefix "test"
- Setup inputs
- Execute code to be tested
- Check output


### Example

app\app\tests.py
``` py
"""
Sample tests
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


app\app\calc.py
``` py
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
``` s
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```


## Database

- PostgresQL
  - Popular open source DB
  - Integrates well with Django
- Docker Compose
  - Defined with project (re-usable)
  - Persistent data using volumes
  - Handles network configuration
  - Environment variable configuration


### Settings for PostgreSQL database

app\app\settings.py
``` py
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

app\app\settings.py
``` py
(...)
INSTALLED_APPS = [
    (...)
    'core',
]
(...)
```


### 3. Create file structure into the core directory:

Files and directories into the **core** project

``` sh
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

app\core\management\commands\wait_for_db.py
``` py
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

app\core\tests\test_commands.py
``` py
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


## Create User Model

The user model is customized, based on Django default user model.



## ... Setup Django Admin ...

...


## ... API Documentation ...

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
``` py
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
``` py
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

``` py
(...)

INSTALLED_APPS = [
  (...)
  'recipe',
]

(...)
```

### 6. Write tests for listing recipes

**6.1. app\recipe\tests\test_recipe_api.py**

``` py
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
``` py
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
``` py
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
``` py
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
``` py
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
``` py
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
``` py
(...)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields = ['description']


```

Modify RecipeViewSet class.

app\recipe\views.py
``` py
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


## Build Tag API

### 1. Tag API Design

#### 1.1. Features

The Tag API will have the following functionalities:

- Add ability do att recipe tags
- Create model for tags
- Add tag API endpoints
- Update recipe endpoint
  - Adding and listing tags

#### 1.2. Tag Model

- name : Name of tag to create
- user : User who created/owns tag

#### 1.3. Endpoints

- /recipes/tags
  - POST - Create new tag
  - PUT/PATCH - Update tags
  - DELETE - Delete tag
  - GET - List all tags


### 3. Write tests for tag model

Create file app\core\tests\test_model_tag.py
``` py
"""
Teste for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class TagModelTests(TestCase):
    """Tests for the Recipe model."""

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)
```

**Run tests (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 4. Create tag model

#### 4.1. Create file

app\core\models\tag.py
``` py
"""
Tag model.
"""
from django.conf import settings
from django.db import models


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
```

#### 4.2. Add the link to the tags o the recipe Model.

Edit file
app\core\models\recipe.py

Ater line:

> link = models.CharField(max_length=255, blank=True)

Add:
``` py
    tags = models.ManyToManyField('Tag')
```

#### 4.3. Import Tag model in \_\_init__.py

Add line in the end of the file
app\core\models\\_\_init__.py
``` py
from .user import User  # noqa: F401
from .user_manager import UserManager  # noqa: F401
from .recipe import Recipe  # noqa: F401
from .tag import Tag  # noqa: F401
```

#### 4.4. Create migrations for the new model

`$ docker-compose run --rm app sh -c "python manage.py makemigrations"`

New migration file is created in
app\core\migrations

**Run tests (Fail, asks to delete "test_devdb")**

`$ docker-compose run --rm app sh -c "python manage.py test"`

Type 'yes' to confirm deletion.


**Run tests (Success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

#### 4.5. Register tag model in Django Admin

Add line to the end of the file
app\core\admin.py

``` py
(...)
admin.site.register(models.Tag)
```

### 6. Create app

(No need for creating app once tags are contained in recipes)

### 6. Write tests for listing tags

Create file
app\recipe\tests\test_tags_api.py
``` py
"""
Tests for tag API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_create_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        Tag.objects.create(user=self.user, name='Drink')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        # many means a list, supressing it will returna single object
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), len(tags))


    def test_test_list_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='otherpass123',
        )
        Tag.objects.create(user=other_user, name='Fruit')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

```

### 7. Implement tag listing API

#### 7.1. Add TagSerializer in recipe serializers.py file

Add to the end of the file
app\recipe\serializers.py
```py
(...)
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
```

#### 7.2. Write Viewset

Edit file
app\revipe\views.py
``` py
(...)
from rest_framework import (
    viewsets,
    mixins,
)
(...)
from core.models import (
    Recipe,
    Tag,
)
(...)
class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override the get queryset method
    def get_queryset(self):
        """Retrieve tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

```

#### 7.4. Add tags router in recipe urls

Add below recipes router registration
app\recipe\urls.py
``` py
(...)
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
(...)
```

**Run tests (Success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`


### 8. Write tests for updating tags

Edit file
app\recipe\tests\test_tags_api.py

Add below
> TAGS_URL = reverse('recipe:tag-list')

and at the end of the file
``` py
TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])

(...)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

```

**Run tests (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 9. Implement update tag API

Update file
app\recipe\views.py

Simply add the parameter **mixins.UpdateModelMixin** to the TagViewSet class.
``` py
class TagViewSet(mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
```

Pay attention to leave the viewset in the last position.

**Run tests (Success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 10. Write tests for deleting tags

Add to the end of file
app\recipe\tests\test_tags_api.py
``` py
    def test_delete_tag(self):
        """Test deleting tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

```

**Run tests (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 11. Implement delete tag API

Update file
app\recipe\views.py

As it was for updating, simply add the parameter **mixins.DestroyModelMixin** to the TagViewSet class.
``` py
class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
```

**Run tests (Success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

## Adding Nested Serializers

- Serializer within a serializer
- Used for fields wich are objects

### 1. Create tests for nested serializers



--- model ---

## Build <Name> API

### 1. <Name> API Design

#### 1.1. Features


#### 1.2. Endpoints

### 3. Write tests for <name> model
### 4. Create <name> model

### 5. Create <name> app
### 6. Write tests for listing <name>s

### 7. Implement <name> listing API

#### 7.1.Create serializers.py file
#### 7.2. Run tests (Fail)

`$ docker-compose run --rm app sh -c "python manage.py test"`


#### 7.3. Write views

app\<name>\views.py
#### 7.4. Add urls

app\<name>\urls.py
#### 7.5. Add urls inside the main urls.py file

**Add to file**

app\app\urls.py
### 8. Write tests for <name>s detail API

Edit file

app\recipe\tests\test_<name>_api.py

...
**Run tests (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 9. Implement <name> detail API

The detail serializer is simply an extension of the <name> serializer.

app\<name>\serializers.py

**Run tests (Success)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 10. Write tests for creating <name>s

(...)

**Run tests (Fail)**

`$ docker-compose run --rm app sh -c "python manage.py test"`

### 11. Implement create <name> API
