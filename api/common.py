import json
from os import getenv


def get_env_var(name, type_=None):

    out = getenv(name, default=None)

    if out is not None:

        try:
            out = json.loads(out)
        except json.JSONDecodeError:
            pass

        if type_ is not None and not isinstance(out, type_):
            raise TypeError(f"The env var {name} is not {repr(type_)}")

        if type_ is list and not all(isinstance(item, str) for item in out):
            raise TypeError(f"The env var {name} must be a list of strings")

    return out
