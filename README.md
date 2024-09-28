
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
```

Activar entorno virtual
```bash
cd on-premise-gpt
poetry shell
```

Instalar dependencias
```bash
poetry install
```
## Ejecutar Localmente

Ir al repositorio del proyecto

```bash
cd on-premise-gpt
```

Iniciar el servidor

```bash
python manage.py runserver
```

Iniciar el servidor de Tailwind CSS

```bash
python manage.py tailwind start
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


## Environment Variables

Para ejecutar este proyecto, agregar las siguientes variables de entorno al archivo .env

`CHROMEDRIVER_FILES_PATH`


## Tech Stack

**Cliente:** [TailwindCSS](https://tailwindcss.com/docs/installation), [Flowbite](https://flowbite.com/docs/getting-started/introduction/), [HTMX](https://htmx.org/docs/), JavaScript

**Servidor:** [Django](https://docs.djangoproject.com/en/5.1/), [django-components](https://github.com/EmilStenstrom/django-components/), [LangChain](https://python.langchain.com/v0.2/docs/integrations/platforms/), [Selenium](https://selenium-python.readthedocs.io/)
