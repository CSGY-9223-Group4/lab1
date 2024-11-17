FROM python:3.12.8-alpine
RUN adduser -D pastebin
WORKDIR /app
RUN chown -R pastebin:pastebin /app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
COPY ./src /app
USER pastebin
CMD ["flask", "run", "--debug"]
