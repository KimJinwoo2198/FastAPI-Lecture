FROM python:3.14-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY app /code/app

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
