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
    docker compose up --build
    ```

### Sample Requests
```bash
# register a new user
$ curl http://localhost:8000/v1/register_user -X POST --data '{"username":"kevin.tarta","password":"ASDFQWER"}' -H 'Content-Type: application/json'
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNzU0Njg4NCwianRpIjoiNmFkMDc5NzMtZjFhMi00ZDY3LTk3MzQtMjdhZmMyMjE2NDdhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VybmFtZSI6ImtldmluLnRhcnRhIiwidXNlcl9pZCI6MTN9LCJuYmYiOjE3Mjc1NDY4ODQsImNzcmYiOiJiMWMwZDlkMi0wNmIwLTQxNmQtOGVhMy00YWUyZDI5MDM4MzIiLCJleHAiOjE3Mjc1NDc3ODR9.DT8QlTTcWtD3mcgUOvS3eYI1V_3Goa_UzZrPY7Gg24k",
  "message": "User registered"
}

# get access token through login endpoint, store in AT
$ AT=$(curl http://localhost:8000/v1/login -X POST --data '{"username":"elveskevtar","password":"ASDFQWER"}' -H 'Content-Type: application/json' | jq '.access_token' -r | tr -d '\n')

# get all notes visible to our new user
$ curl -H "Authorization: Bearer $AT" -H "Content-Type: application/json" http://localhost:8000/v1/notes -v
[
  {
    "author": "kevin.tarta",
    "created_at": "2024-09-25T23:46:27",
    "note_id": 4,
    "public": false,
    "text": "private secret here",
    "title": "CONFIDENTIAL",
    "updated_at": "2024-09-25T23:59:10"
  }
]

# get a single note
$ curl -H "Authorization: Bearer $AT" -H "Content-Type: application/json" http://localhost:8000/v1/notes/4 -v
[
  {
    "author": "kevin.tarta",
    "created_at": "2024-09-25T23:46:27",
    "note_id": 4,
    "public": false,
    "text": "private secret here",
    "title": "CONFIDENTIAL",
    "updated_at": "2024-09-25T23:59:10"
  }
]

# update the note
$ curl -H "Authorization: Bearer $AT" -H "Content-Type: application/json" http://localhost:8000/v1/notes/4 -X PUT -H 'Content-Type: application/json' --data '{"title": "CONFIDENTIAL", "text": "updating my secret"}'
[
  {
    "author": "kevin.tarta",
    "created_at": "2024-09-25T23:46:27",
    "note_id": 4,
    "public": false,
    "text": "updating my secret",
    "title": "CONFIDENTIAL",
    "updated_at": "2024-09-28T18:13:50"
  }
]

# creating a new note
$ curl -H "Authorization: Bearer $AT" -H "Content-Type: application/json" http://localhost:8000/v1/notes -X POST -H 'Content-Type: application/json' --data '{"title": "CONFIDENTIAL", "text": "new secret!!"}'
{
  "author": "kevin.tarta",
  "created_at": "2024-09-28T18:14:54",
  "note_id": 7,
  "public": false,
  "text": "new secret!!",
  "title": "CONFIDENTIAL",
  "updated_at": "2024-09-28T18:14:54"
}

# deleting a note
$ curl -H "Authorization: Bearer $AT" -H "Content-Type: application/json" http://localhost:8000/v1/notes/7 -X DELETE
{
  "message": "Successfully deleted note 7"
}
```

## Technical Design

### API
| Request | Response |
| ------- | -------- |
| POST /v1/register_user<br>{<br>&nbsp;&nbsp;"username": "ASDF",<br>&nbsp;&nbsp;"password": "QWER"<br>} | 200 OK<br>{<br>&nbsp;&nbsp;"message": "User registered",<br>&nbsp;&nbsp;"access_token": "&lt;JWT_ACCESS_TOKEN&gt;"<br>}<br>400 Bad Request<br>415 Unsupported Media Type (not JSON)<br>409 Conflict (User already exists)<br>500 Internal Server Error |
| POST /v1/login<br>{<br>&nbsp;&nbsp;"username": "ASDF",<br>&nbsp;&nbsp;"password": "QWER"<br>} | 200 OK<br>{<br>&nbsp;&nbsp;"access_token": "&lt;JWT ACCESS TOKEN&gt;"<br>}<br>400 Bad Request<br>415 Unsupported Media Type (not JSON)<br>401 Unauthorized (Invalid username or password)<br>500 Internal Server Error |
| GET /v1/protected<br>Authorization: Bearer <JWT_ACCESS_TOKEN> | 200 OK<br>{<br>&nbsp;&nbsp;"logged_in_as": {<br>&nbsp;&nbsp;&nbsp;&nbsp;"user_id": 1234,<br>&nbsp;&nbsp;&nbsp;&nbsp;"username": "ASDF"<br>&nbsp;&nbsp;}<br>}<br>500 Internal Server Error |
| GET /v1/notes[?page=1&page_size=10]<br>Authorization: Bearer <JWT_ACCESS_TOKEN> | 200 OK<br>[<br>&nbsp;&nbsp;{<br>&nbsp;&nbsp;&nbsp;&nbsp;"author": "ASDF",<br>&nbsp;&nbsp;&nbsp;&nbsp;"created_at": "2024-09-25T23:46:27",<br>&nbsp;&nbsp;&nbsp;&nbsp;"note_id": 4,<br>&nbsp;&nbsp;&nbsp;&nbsp;"public": false,<br>&nbsp;&nbsp;&nbsp;&nbsp;"text": "This is a personal, private note",<br>&nbsp;&nbsp;&nbsp;&nbsp;"title": "CONFIDENTIAL, do not read",<br>&nbsp;&nbsp;&nbsp;&nbsp;"updated_at": "2024-09-25T23:59:10"<br>&nbsp;&nbsp;}<br>]<br>400 Bad Request<br>401 Unauthorized<br>500 Internal Server Error |
| GET /v1/notes/&lt;int:note_id&gt;<br>Authorization: Bearer <JWT_ACCESS_TOKEN> | 200 OK<br>{<br>&nbsp;&nbsp;"author": "ASDF",<br>&nbsp;&nbsp;"created_at": "2024-09-25T23:46:27",<br>&nbsp;&nbsp;"note_id": 4,<br>&nbsp;&nbsp;"public": false,<br>&nbsp;&nbsp;"text": "This is a personal, private note",<br>&nbsp;&nbsp;"title": "CONFIDENTIAL, do not read",<br>&nbsp;&nbsp;"updated_at": "2024-09-25T23:59:10"<br>}<br>400 Bad Request<br>401 Unauthorized<br>404 Not Found<br>500 Internal Server Error |
| POST /v1/notes<br>Authorization: Bearer <JWT_ACCESS_TOKEN><br>{<br>&nbsp;&nbsp;"title": "CONFIDENTIAL, do not read",<br>&nbsp;&nbsp;"text": "This is a personal, private note",<br>&nbsp;&nbsp;"public": false<br>} | 201 Created<br>{<br>&nbsp;&nbsp;"author": "ASDF",<br>&nbsp;&nbsp;"created_at": "2024-09-25T23:46:27",<br>&nbsp;&nbsp;"note_id": 4,<br>&nbsp;&nbsp;"public": false,<br>&nbsp;&nbsp;"text": "This is a personal, private note",<br>&nbsp;&nbsp;"title": "CONFIDENTIAL, do not read",<br>&nbsp;&nbsp;"updated_at": "2024-09-25T23:59:10"<br>}<br>400 Bad Request<br>401 Unauthorized<br>415 Unsupported Media Type<br>500 Internal Server Error |
| PUT /v1/notes/&lt;int:note_id&gt;<br>Authorization: Bearer <JWT_ACCESS_TOKEN><br>{<br>&nbsp;&nbsp;"title": "CONFIDENTIAL, do not read",<br>&nbsp;&nbsp;"text": "This is a personal, private note",<br>&nbsp;&nbsp;"public": false<br>} | 200 OK<br>{<br>&nbsp;&nbsp;"author": "ASDF",<br>&nbsp;&nbsp;"created_at": "2024-09-25T23:46:27",<br>&nbsp;&nbsp;"note_id": 4,<br>&nbsp;&nbsp;"public": false,<br>&nbsp;&nbsp;"text": "This is a personal, private note",<br>&nbsp;&nbsp;"title": "CONFIDENTIAL, do not read",<br>&nbsp;&nbsp;"updated_at": "2024-09-25T23:59:10"<br>}<br>400 Bad Request<br>401 Unauthorized<br>415 Unsupported Media Type<br>500 Internal Server Error |
| DELETE /v1/notes/&lt;int:note_id&gt;<br>Authorization: Bearer <JWT_ACCESS_TOKEN> | 200 OK<br>{<br>&nbsp;&nbsp;"message": "Successfully deleted note 4"<br>}<br>400 Bad Request<br>401 Unauthorized<br>500 Internal Server Error |

### Database
MySQL
```sql
CREATE TABLE `users` (
    `user_id` INT(11) AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uniq_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `notes` (
    `note_id` INT(11) AUTO_INCREMENT PRIMARY KEY,
    `note_title` VARCHAR(255) NOT NULL,
    `note_text` TEXT NOT NULL,
    `is_public` BOOLEAN NOT NULL DEFAULT FALSE,
    `author_id` INT(11) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_author_id` (`author_id`),
    CONSTRAINT `fk_notes_author_id`
        FOREIGN KEY (`author_id`)
        REFERENCES `users`(`user_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
