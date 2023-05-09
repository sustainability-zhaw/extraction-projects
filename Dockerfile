FROM python:3.11.1-slim-bullseye

COPY requirements.txt /requirements.txt

WORKDIR /app

RUN pip install -r /requirements.txt && \
    rm /requirements.txt && \
    groupadd -r app && \
    useradd --no-log-init -r -g app app && \
    chmod -R 775 /app

COPY src/ /app/

USER app

EXPOSE 8080

CMD [ "python", "main.py" ]
