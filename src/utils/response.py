import json
class Response:
    SUCCESS_CODE = 200
    ERROR_CODE = 500
    def __init__(self, code, data, message):
        self.code = code
        self.data = data
        self.message = message
    
    def to_dict(self):
        return {
            "code": self.code,
            "data": self.data,
            "message": self.message
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    @staticmethod
    def success(data, message):
        return Response(Response.SUCCESS_CODE, data, message).to_dict()
    
    @staticmethod
    def error(message):
        return Response(Response.ERROR_CODE, None, message).to_dict()
        