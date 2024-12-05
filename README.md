
# On Premise GPT

Chatbot para responder preguntas sobre leyes contenidas en el Digesto Jurídico Nicaraguense


## Instalación
Instalar [pipx](https://pipx.pypa.io/stable/installation/) en ubuntu
```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

Instalar el gestor de dependencias [Poetry](https://python-poetry.org/docs/#installation)
```bash
pipx install poetry
source ~/.bashrc
```

Activar entorno virtual
```bash
poetry shell
```

Instalar dependencias
```bash
poetry install
```

Instalar Milvus DB
```bash
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
```

Iniciar Contenedor de Docker
```bash
$ bash standalone_embed.sh start
```



## Ejecutar Localmente


Crea un API KEY de Google Gemini en el siguiente enlace: https://aistudio.google.com/

Crear un archivo .env con las siguientes variables de entorno

`CHROMEDRIVER_FILES_PATH`

`GEMINI_API_KEY`

Instalar dependencias de Tailwind CSS

```bash
python manage.py tailwind install
```

Iniciar el servidor de Tailwind CSS

```bash
python manage.py tailwind start
```

Iniciar el servidor de Django

```bash
python manage.py runserver
```

Iniciar el servidor de FastAPI
```bash
cd fastapi_services
```

```bash
uvicorn embedding_service:app --reload --port 8080
```


## Commits

### pre-commit hooks
Ejecutar pre-commit hooks con el siguiente comando
```bash
pre-commit run --all-files
```

## Script de web scraping

### Instalar la última version de Chrome for Testing (Linux)
Instalar jq para Ubuntu/Debian
```bash
sudo apt install jq
```

Descargar la última versión Chrome
```bash
meta_data=$(curl 'https://googlechromelabs.github.io/chrome-for-testing/\
last-known-good-versions-with-downloads.json')
wget $(echo "$meta_data" | jq -r '.channels.Stable.downloads.chrome[0].url')
```

Instalar dependencias de Chrome
```bash
sudo apt install ca-certificates fonts-liberation \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 \
    libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 \
    libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 \
    libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils -y
```

Descomprimir el archivo
```bash
unzip chrome-linux64.zip
```

### Instalar versión compatible de Chromedriver

Descargar el archivo de Chromedriver con el siguiente comando

```bash
meta_data=$(curl 'https://googlechromelabs.github.io/chrome-for-testing/\
last-known-good-versions-with-downloads.json')
wget $(echo "$meta_data" | jq -r '.channels.Stable.downloads.chromedriver[0].url')
```

Descomprimir el archivo

```bash
unzip chromedriver-linux64.zip
```

Añadir el directorio absoluto donde se hayan descargado los archivos a las variables de entorno

```bash
CHROMEDRIVER_FILES_PATH=/path/to/files
```

### Descargar leyes de la web del Digesto Jurídico

Para iniciar la descarga ejecutar el siguiente comando
```bash
python manage.py shell < apps/digest_data/utils/digest_laws/download_all_laws.py
```

## Django Scripts

### Manejo de Usuarios

Crear un super usuario
```bash
python manage.py createsuperuser
```

### Migraciones de Base de Datos

Crear migraciones
```bash
python manage.py makemigrations
```

Ejecutar migraciones
```bash
python manage.py migrate
```

### Django Components

Ejecutar el siguiente comando para crear un componente utilizando [django-component]('https://github.com/EmilStenstrom/django-components/')

```bash
python manage.py startcomponent component_name
```

### Traducciones

Ejecutar el siguiente comando para preparar las traducciones en los archivos JavaScript
```bash
django-admin makemessages --all --ignore=env --extension=js --domain=djangojs  --ignore=apps/theme
```

Ejecutar el siguiente comando para preparar las traducciones en los archivos HTML
```bash
django-admin makemessages --all --ignore=env
```

Ejecutar el siguiente comando para compilar las traducciones
```bash
django-admin compilemessages --ignore=env
```

**Estos comandos se ejecutan cada que se inicia el proyecto de Django**

## Tech Stack

**Cliente:** [TailwindCSS](https://tailwindcss.com/docs/installation), [Flowbite](https://flowbite.com/docs/getting-started/introduction/), [HTMX](https://htmx.org/docs/), JavaScript

**Servidor:** [Django](https://docs.djangoproject.com/en/5.1/), [django-components](https://github.com/EmilStenstrom/django-components/), [LangChain](https://python.langchain.com/v0.2/docs/integrations/platforms/), [Selenium](https://selenium-python.readthedocs.io/)
