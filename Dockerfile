FROM python:3.11

WORKDIR /dtcgweb/

COPY ./requirements.txt /dtcgweb/requirements.txt
COPY ./pyproject.toml /dtcgweb/pyproject.toml
COPY ./README.md /dtcgweb/README.md
COPY ./LICENSE /dtcgweb/LICENSE
COPY ./src/dockerception /dtcgweb/dockerception/
COPY ./src/dockerception/static/ /dtcgweb/static/

# RUN pip install --no-cache-dir --upgrade -e .
RUN pip install --upgrade -e .

WORKDIR /dtcgweb/dockerception/
CMD ["fastapi", "run", "app.py", "--proxy-headers", "--port", "8080"]