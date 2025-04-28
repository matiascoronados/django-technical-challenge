# django-technical-challenge

## 1. Configurar
### 1.1 Pre-requisitos 
Para configurar el proyecto es necesario tener instalado Python. Preferiblemente la version 3.10

### 1.2 Configurar el proyecto.
Para configurar las dependencias del proyecto se deben utilizar los siguientes comandos.
1. pip install django
2. pip install djangorestframework
3. pip install drf-spectacular

### 1.3 Migrar datos de los modelos.
Una vez configurado lo anterior, en la carpeta raiz del proyecto "DJANGO-TECHNICAL-CHALLENGE" se deben ejecutar lo siguientes comandos:
1. python manage.py makemigrations
2. python manage.py migrate

## 2. Ejecutar
Para ejecutar el servidor basta con poner en consola el comando.
1. python manage.py runserver

Para ejecutar las pruebas se debe por en consola el comando.
1. python manage.py test enrichment_logic

## 3. Utilizar
Acceder a la URL que se muestra por consola, usualmente es http://127.0.0.1:8000/. Al ingresar aparecera un swagger los apartados:
1. "Category" para el CRUD de la Categoria.
2. "Keywords" para el CRUD de los Keywords.
3. "Merchant" para el CRUD de los Comercios.
4. "Enrichment" para el endpoint con la logica principal del sistema.