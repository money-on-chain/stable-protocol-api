


def make_responses(*args):

    responses = {}

    for arg in args:

        try:
            code, description = arg
        except TypeError:
            code, description = arg, None
        
        assert(isinstance(code, int))

        if description is None:
            description = {
                503: "Service Unavailable",
                400: "Bad Request",
                404: "Not found"                
            }.get(code, None)

        responses[code] = {"description": description,
            "content": {
                "application/json": {
                    "example": {"detail": description}}}}

    return responses
