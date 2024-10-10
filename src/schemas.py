from marshmallow import Schema, fields, validate

class PreAllocateDocumentsRequestSchema(Schema):
    department_id = fields.Int(required=True)
    count = fields.Int(required=True, validate=validate.Range(min=1, max=250))
    issuing_authority = fields.String(required=True, validate=validate.Length(min=1, max=120))
    summary = fields.String(required=True, validate=validate.Length(min=1, max=250))
    direction = fields.String(load_default='in', validate=validate.OneOf(['in', 'out']))
    dry_run = fields.Bool(load_default=False)

class PreAllocateDocumentsResponseSchema(Schema):
    department_id = fields.Int(required=True)
    count = fields.Int(required=True, validate=validate.Range(min=1, max=250))
    issuing_authority = fields.String(required=True, validate=validate.Length(min=1, max=120))
    summary = fields.String(required=True, validate=validate.Length(min=1, max=250))
    create_at = fields.DateTime(required=True)
    document_id = fields.List(fields.String, required=True)
    year = fields.Int(required=True)
    direction = fields.String(required=True, validate=validate.OneOf(['in', 'out']))
    