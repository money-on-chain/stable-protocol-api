def mongo_date_to_str(x):
    if not x:
        return None
    return str(x.isoformat(timespec='milliseconds'))+"Z"


def fields_date_to_str(fields, fields_date):

    for field_date in fields_date:
        v_date = field_date.split('.')
        if len(v_date) > 1:
            try:
                fields[v_date[0]][v_date[1]] = mongo_date_to_str(fields[v_date[0]][v_date[1]])
            except KeyError:
                pass
        else:
            try:
                fields[field_date] = mongo_date_to_str(fields[field_date])
            except KeyError:
                pass

    return fields
