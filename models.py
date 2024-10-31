from marshmallow import Schema, fields

class HistorySchema(Schema):
    option = fields.String(required=True, error_messages={"required": "'option' necessário"})
    start_date = fields.Date(required=False, format="%d-%m-%Y", missing="all")
    end_date = fields.Date(required=False, format="%d-%m-%Y", missing="all")