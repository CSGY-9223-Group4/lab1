# CS-GY 9223 Practical Software Supply Chain Security Lab 1
[Lab One: Source](https://docs.google.com/document/d/1JerGq5ahuI2IfSe3ops0aVp8_xvRojpZKvuFdxADXw8/edit)

## Usage
1. Create secrets using Docker
    ```bash
    echo "JWT_SECRET=`openssl rand -base64 32`" >> .env
    echo "DB_PASSWORD=`openssl rand -base64 20`" >> .env
    echo "DB_ROOT_PASSWORD=`openssl rand -base64 20`" >> .env
    ```
2. Start containers
    ```bash
    docker compose up
    ```

## Technical Design

### API
TBD

### Database
TBD
