from os import getenv


def get_env_var(name, type_=None):
    
    out = getenv(name, default=None)
    
    if out is not None:

        try:
            out = eval(out, {}, {})
        except Exception as e:
            out = str(out)
        
        if type_ is not None and not isinstance(out, type_):
            raise TypeError(f"The env var {name} is not {repr(type_)}")

    return out
