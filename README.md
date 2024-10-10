export FLASK_ENV=development
export FLASK_APP=app.py
export PYTHONPATH=src 

flask run

# Deployment

Some operations are basic authentication protected. 

To allow authenticating a new user, define an ENV value with
the `BASIC_AUTH_{username}` pattern (case sensitive) and value a `sha256` hash of the desired password.

Tip: On Unix systems, you can obtain the hash with the following command : 

```bash
$ echo -n "password" | sha256
5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
```

## Retrieve Document

The API endpoint retrieves an existing document

### Endpoint URI

`/api/v1.0/document/{year}/{p_id}`

### Path parameters


| Name | Type | Required |  Required |
| - | - | - | - |
| `year` | `int` | yes | The year of the document expressed as `yyyy` |
| `p_id` | `int` | yes | The ID of the document |

### Query parameters

None

### HTTP Responses

| Status | Description
| - | - |
| `200` | Document found and returned
| `404` | Document not found


### Payload Schema

The payload, in case of success, consists of single `document` object defined as : 

* `associated_departments` [`list`] - a list of associated/assigned departments. Each "associated department" consists of the following attributes : 
    * `accept_time` [`datetime`] - when the department accepted the assignment
    * `assigned_on` [`datetime`] - when the assigment took place 
    * `fullname` [`string`] - the full name of the department
    * `username` [`string`] - the username of the department

* `cc` [`string`] -
* `comments` [`string`] -
* `completed` [`string`] -
* `date` [`string`] -
* `direction` [`string`] -
* `folder_archive_date` [`string`] -
* `folder_archive_id` [`string`] -
* `p_id` [`string`] -
* `issuing_authority` [`string`] -
* `issuing_authority_date` [`string`] -
* `issuing_authority_id` [`string`] -
* `issuing_authority_place` [`string`] -
* `summary` [`string`] -
* `last_modified` [object] - 
    * `modified_by_fullname` 
    * `modified_by_username`
    * `modified_on_date`

### Example Responses

#### Success

```json
{
    "payload": {
        "document": {
            "associated_departments": [
                {
                    "accept_time": null,
                    "assigned_on": "2024-01-04T14:52:43",
                    "fullname": "XXXXXX YYYYY",
                    "username": "YYYYYY"
                },
                {
                    "accept_time": null,
                    "assigned_on": "2024-01-04T14:52:43",
                    "fullname": "XXXXXXX YYYYY",
                    "username": "XXXXXX"
                }
            ],
            "cc": "",
            "comments": "",
            "completed": true,
            "date": "2024-01-04",
            "direction": "in",
            "folder_archive_date": "2024-01-26",
            "folder_archive_id": "Φ.ΕΞ` ΑΛ.ΠΕΡΙΦ.",
            "id": 110,
            "incoming_mail": {
                "date": "2024-01-04 13:12:31",
                "from": "Δ/Υ",
                "subject": " Χορήγηση αναρρωτικής άδειας XXXXXX YYYYYY"
            },
            "issuing_authority": "SCH.GR ΓΡΑΦΕΙΟ ΣΥΝΔΕΣΜΟΥ ΕΚΠΑΙΔΕΥΣΗΣ ΝΤΙΣΕΛΝΤΟΡΦ",
            "issuing_authority_date": "2024-01-04",
            "issuing_authority_id": null,
            "issuing_authority_place": "Αθήνα",
            "last_modified": {
                "modified_by_fullname": "XXXXXX YYYYYY",
                "modified_by_username": "YYYYYY",
                "modified_on_date": "2024-01-26T11:22:15"
            },
            "summary": "Χορήγηση αναρρωτικής άδειας XXXXXX YYYYY"
        }
    },
    "success": true
}
```


#### Failure

```json
{
    "error": "document \"110111\" was not found",
    "success": false
}
```


## Retrieve Departments

The API endpoint searches for departments based on query string that partially matches the department's name

### Endpoint URI

`/api/v1.0/departments`

### Path parameters

None

### Query parameters

| Name | Type | Required |  Description |
| - | - | - | - |
| `name` | `str` | yes | filter by name |


### HTTP Responses

| Status | Description
| - | - |
| `200` | Request was successfull
| `500` | Error during execution


### Payload Schema

On success the endpoint returns the following response

```json
{
    "payload": {
        "departments": [
            {
                "description": "Σλάβικ Φίλιππος",
                "id": 2,
                "name": "Μηχανογράφηση (Σλάβικ Φίλιππος)"
            }
        ],
        "page_number": 1,
        "page_size": 25,
        "total_departments": 1
    },
    "success": true
}
```

On failure the following will be returned : 

```json
{
    "code": 500,
    "description": "An unexpected error occurred. Please try again later.",
    "error": "Internal Server Error",
    "success": false
}
```

## Preallocate Documents

The endpoint will allow you to pre-allocate a block of incomming
or outgoing documents in the current year.

Note, the operation is protected with basic authentication.

### Endpoint URI

`/api/v1.0/document/preallocate`

### Path parameters

None

### Query parameters

None

### Request Body

Request body needs to be a JSON document with the following params :

| Name | Type | Required |  Default | Description |
| - | - | - | - | - |
| `department_id` | `int` | yes |  | The ID of the department that wll be associated with the pre-allocated documents |
| `count` | `int` | yes |  | The number of documents to pre-allocate |
| `issuing_authority` | `str` | yes |  | The issuing authority that will be used when pre-allocating the documents |
| `summary` | `str` | yes |  | The summary that will be used when pre-allocating the documents |
| `direction` | `str` | yes | `in` | The direction (type) of the pre-allocated documents. The value can be `in` or `out` |
| `dry_run` | `bool` | no | `false` | If set to `true`, then the pre-allocated documents will not be actually stored in the database |
    

### HTTP Responses

| Status | Description
| - | - |
| `201` | Request was successfull, documents stored in DB
| `404` | Bad request (request was not validated)
| `500` | Error during execution


### Payload Schema

Assuming the request is the follwing : 

```json
{
    "department_id": 77,
    "count": 5,
    "issuing_authority": "ΣΛΑΒΙΚ",
    "summary": "ΚΑΠΟΙΟ ΘΕΜΑ",
    "direction": "in",
}
```

then, the endpoint returns the following response

```json
{
    "count": 5,
    "create_at": "2024-10-10T08:43:03.575307+03:00",
    "department_id": 77,
    "direction": "in",
    "document_id": [
        "10735",
        "10736",
        "10737",
        "10738",
        "10739"
    ],
    "issuing_authority": "ΣΛΑΒΙΚ",
    "summary": "ΚΑΠΟΙΟ ΘΕΜΑ",
    "year": 2024
}
```

On invalid request (in this case the `count` attribute of the request body was invalid), the following response will be returned : 

```json
{
    "code": 400,
    "description": {
        "validation_errors": {
            "count": [
                "Not a valid integer."
            ]
        }
    },
    "error": "Bad Request",
    "success": false
}
```

On failure the following will be returned : 

```json
{
    "code": 500,
    "description": "An unexpected error occurred. Please try again later.",
    "error": "Internal Server Error",
    "success": false
}
```