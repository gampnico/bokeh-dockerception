FROM python:3.11


WORKDIR /app


COPY ./requirements.txt /app/requirements.txt
COPY ./pyproject.toml /app/pyproject.toml
COPY ./README.md /app/README.md
COPY ./LICENSE /app/LICENSE
COPY ./src/dockerception /app/dockerception/
COPY ./src/dockerception/static/ /app/static/

RUN pip install --no-cache-dir --upgrade -e .


CMD ["fastapi", "run", "dockerception/app.py", "--proxy-headers", "--port", "8080"]