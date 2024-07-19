export FLASK_ENV=development
export FLASK_APP=app.py
export PYTHONPATH=src 

flask run

# Retrieve Document

The API endpoint retrieves an existing document

## Endpoint URI

`/api/v1.0/document/{year}/{p_id}`

## Path parameters


| Name | Type | Required |  Required |
| - | - | - | - |
| `year` | `int` | yes | The year of the document expressed as `yyyy` |
| `p_id` | `int` | yes | The ID of the document |

## Query parameters

None

## HTTP Responses

| Status | Description
| - | - |
| `200` | Document found and returned
| `404` | Document not found

## Example Responses

### Success

```json
{
    "payload": {
        "document": {
            "associated_departments": [
                {
                    "accept_time": null,
                    "assigned_on": "2024-01-04T14:52:43",
                    "fullname": "Αυγουστάκη Γεωργία",
                    "username": "avgoustaki"
                },
                {
                    "accept_time": null,
                    "assigned_on": "2024-01-04T14:52:43",
                    "fullname": "Θώμου Ήβη",
                    "username": "thomou"
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
                "subject": " Χορήγηση αναρρωτικής άδειας Μαρκατάτος Νικόλαος"
            },
            "issuing_authority": "SCH.GR ΓΡΑΦΕΙΟ ΣΥΝΔΕΣΜΟΥ ΕΚΠΑΙΔΕΥΣΗΣ ΝΤΙΣΕΛΝΤΟΡΦ",
            "issuing_authority_date": "2024-01-04",
            "issuing_authority_id": null,
            "issuing_authority_place": "Αθήνα",
            "last_modified": {
                "modified_by_fullname": "Αλεξάκη Αικατερίνη",
                "modified_by_username": "alexaki",
                "modified_on_date": "2024-01-26T11:22:15"
            },
            "summary": "Χορήγηση αναρρωτικής άδειας Μαρκατάτος Νικόλαος"
        }
    },
    "success": true
}
```


### Failure

```json
{
    "error": "document \"110111\" was not found",
    "success": false
}
```