


def make_responses(*args):

    responses = {}

    for arg in args:

        try:
            code, data = arg
        except TypeError:
            code, data = arg, None
        
        assert(isinstance(code, int))

        if data is None:
            data = {
                503: "Service Unavailable",
                400: "Bad Request",
                404: "Not found"                
            }.get(code, None)

        if isinstance(data, str):
            responses[code] = {"description": data,
                "content": {
                    "application/json": {
                        "example": {"detail": data}}}}
        else:
            responses[code] = data

    return responses
