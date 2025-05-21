# Database Schema

## Table: CouncilInfo

| Column Name     | Data Type        | Constraints        | Nullable | Description                                   |
|-----------------|------------------|--------------------|----------|-----------------------------------------------|
| id              | INTEGER          | PRIMARY KEY        | No       | Unique identifier for the council information |
| introduction    | TEXT             |                    | Yes      | Introduction to the council                   |
| mission         | TEXT             |                    | Yes      | Council's mission statement                   |
| history         | TEXT             |                    | Yes      | History of the council                        |
| vision          | TEXT             |                    | Yes      | Council's vision statement                    |
| goals           | TEXT             |                    | Yes      | Council's goals                               |
| last_updated_by | INTEGER          | FOREIGN KEY (Users.id) | Yes      | User who last updated the record              |
| last_updated_at | TIMESTAMP        |                    | Yes      | Timestamp of the last update                  |

## Table: Members

| Column Name     | Data Type        | Constraints        | Nullable | Description                             |
|-----------------|------------------|--------------------|----------|-----------------------------------------|
| id              | INTEGER          | PRIMARY KEY        | No       | Unique identifier for the member        |
| name            | VARCHAR(255)     |                    | No       | Member's name                           |
| role            | VARCHAR(255)     |                    | Yes      | Member's role in the council            |
| bio             | TEXT             |                    | Yes      | Short biography of the member           |
| image_url       | VARCHAR(255)     |                    | Yes      | URL to the member's image               |
| display_order   | INTEGER          |                    | Yes      | Order in which members are displayed    |
| last_updated_by | INTEGER          | FOREIGN KEY (Users.id) | Yes      | User who last updated the record        |
| last_updated_at | TIMESTAMP        |                    | Yes      | Timestamp of the last update            |

## Table: Services

| Column Name     | Data Type        | Constraints        | Nullable | Description                                  |
|-----------------|------------------|--------------------|----------|----------------------------------------------|
| id              | INTEGER          | PRIMARY KEY        | No       | Unique identifier for the service            |
| name            | VARCHAR(255)     |                    | No       | Name of the service                          |
| description     | TEXT             |                    | Yes      | Detailed description of the service          |
| type            | VARCHAR(100)     |                    | Yes      | Type of service (e.g., informational, form-based) |
| last_updated_by | INTEGER          | FOREIGN KEY (Users.id) | Yes      | User who last updated the record             |
| last_updated_at | TIMESTAMP        |                    | Yes      | Timestamp of the last update                 |

## Table: ServiceSubmissions

| Column Name        | Data Type        | Constraints           | Nullable | Description                                      |
|--------------------|------------------|-----------------------|----------|--------------------------------------------------|
| id                 | INTEGER          | PRIMARY KEY           | No       | Unique identifier for the submission             |
| service_id         | INTEGER          | FOREIGN KEY (Services.id) | No       | Linked service                                   |
| user_name          | VARCHAR(255)     |                       | No       | Name of the user submitting the service request  |
| user_contact       | VARCHAR(255)     |                       | No       | Contact information of the user (email/phone)    |
| submission_content | TEXT             |                       | Yes      | Content/details of the submission                |
| status             | VARCHAR(50)      |                       | No       | Status of the submission (e.g., pending, approved, rejected) |
| submission_date    | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP | No       | Date and time of submission                      |
| remarks            | TEXT             |                       | Yes      | Any remarks or notes on the submission           |
| last_updated_by    | INTEGER          | FOREIGN KEY (Users.id)  | Yes      | User who last updated the record                 |
| last_updated_at    | TIMESTAMP        |                       | Yes      | Timestamp of the last update                     |

## Table: DivisionsAndCommittees

| Column Name     | Data Type        | Constraints        | Nullable | Description                                     |
|-----------------|------------------|--------------------|----------|-------------------------------------------------|
| id              | INTEGER          | PRIMARY KEY        | No       | Unique identifier for the division/committee    |
| name            | VARCHAR(255)     |                    | No       | Name of the division or committee               |
| description     | TEXT             |                    | Yes      | Description of the division or committee        |
| type            | VARCHAR(50)      |                    | No       | Type (division or committee)                    |
| last_updated_by | INTEGER          | FOREIGN KEY (Users.id) | Yes      | User who last updated the record                |
| last_updated_at | TIMESTAMP        |                    | Yes      | Timestamp of the last update                    |

## Table: Documents

| Column Name      | Data Type        | Constraints        | Nullable | Description                                    |
|------------------|------------------|--------------------|----------|------------------------------------------------|
| id               | INTEGER          | PRIMARY KEY        | No       | Unique identifier for the document             |
| title            | VARCHAR(255)     |                    | No       | Title of the document                          |
| description      | TEXT             |                    | Yes      | Description of the document                    |
| file_path_or_url | VARCHAR(255)     |                    | No       | Filesystem path or URL to the document         |
| category         | VARCHAR(100)     |                    | Yes      | Category of the document (e.g., form, notice, budget) |
| publication_date | DATE             |                    | Yes      | Date when the document was published           |
| last_updated_by  | INTEGER          | FOREIGN KEY (Users.id) | Yes      | User who last updated the record               |
| last_updated_at  | TIMESTAMP        |                    | Yes      | Timestamp of the last update                   |

## Table: NewsAndEvents

| Column Name       | Data Type        | Constraints        | Nullable | Description                                      |
|-------------------|------------------|--------------------|----------|--------------------------------------------------|
| id                | INTEGER          | PRIMARY KEY        | No       | Unique identifier for the news/event item        |
| title             | VARCHAR(255)     |                    | No       | Title of the news or event                       |
| content           | TEXT             |                    | No       | Content/description of the news or event         |
| date              | DATE             |                    | No       | Date of the news or event                        |
| type              | VARCHAR(50)      |                    | No       | Type (news or event)                             |
| image_url         | VARCHAR(255)     |                    | Yes      | URL for an accompanying image                    |
| video_url         | VARCHAR(255)     |                    | Yes      | URL for an accompanying video                    |
| last_updated_by   | INTEGER          | FOREIGN KEY (Users.id) | Yes      | User who last updated the record                 |
| last_updated_at   | TIMESTAMP        |                    | Yes      | Timestamp of the last update                     |

## Table: Users

| Column Name     | Data Type        | Constraints        | Nullable | Description                               |
|-----------------|------------------|--------------------|----------|-------------------------------------------|
| id              | INTEGER          | PRIMARY KEY        | No       | Unique identifier for the user            |
| username        | VARCHAR(255)     | UNIQUE             | No       | Username for login                        |
| hashed_password | VARCHAR(255)     |                    | No       | Hashed password for security              |
| role            | VARCHAR(50)      |                    | No       | Role of the user (e.g., admin, editor)    |
| created_at      | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP | No       | Timestamp of user creation                |

## Table: ContentTranslations

| Column Name     | Data Type        | Constraints                                     | Nullable | Description                                                        |
|-----------------|------------------|-------------------------------------------------|----------|--------------------------------------------------------------------|
| id              | INTEGER          | PRIMARY KEY                                     | No       | Unique identifier for the translation                              |
| table_name      | VARCHAR(255)     |                                                 | No       | Name of the table containing the original record (e.g., 'Services', 'NewsAndEvents') |
| record_id       | INTEGER          |                                                 | No       | Primary key of the record in `table_name` that is being translated |
| language_code   | VARCHAR(5)       |                                                 | No       | Language code for the translation (e.g., 'si', 'ta', 'en')         |
| field_name      | VARCHAR(255)     |                                                 | No       | Name of the field in `table_name` that is being translated       |
| translated_text | TEXT             |                                                 | No       | The translated text content                                        |
| last_updated_by | INTEGER          | FOREIGN KEY (Users.id)                          | Yes      | User who last updated or approved the translation                  |
| last_updated_at | TIMESTAMP        |                                                 | Yes      | Timestamp of the last update                                       |
| **Composite Unique Key** |          | (table_name, record_id, language_code, field_name) |          | Ensures a unique translation for each field in each language       |

**General Notes:**

*   `TEXT` data type is used for potentially long strings. `VARCHAR(255)` is a common choice for shorter strings. Adjust lengths as needed.
*   `TIMESTAMP` can be used for `datetime` storage. `DATE` for date only.
*   `last_updated_by` columns link to the `Users` table to track who made changes.
*   `last_updated_at` columns should ideally be updated automatically on record modification.
*   The `ContentTranslations` table uses a composite unique key to ensure that for any given record in any table, a specific field can only have one translation per language.
*   Consider adding indexes to foreign key columns and frequently queried columns for performance.
*   `display_order` in `Members` can be used to control the order of appearance.
*   `remarks` in `ServiceSubmissions` can be used by admins to add notes regarding the submission.
*   `created_at` in `Users` tracks when a user account was created.
*   The `ContentTranslations.record_id` does not have a direct FOREIGN KEY constraint in this schema because it needs to refer to different tables. This relationship would typically be enforced at the application level or through triggers if the database supports it.
