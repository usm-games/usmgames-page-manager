from flask import jsonify

errors = {
    'ALREADY_SUBMITTED': (400, 'You have already made a submission for this challenge'),
    'ALREADY_EVALUATED': (400, 'This submission has already been evaluated'),
    'NOT_EVALUATED': (400, 'This submission has not been evaluated yet'),
    'INVALID_URL': (400, 'Data has an invalid URL'),
    'MISSING_FIELDS': (400, 'The given data is missing some fields'),
    'NO_ASSOCIATED_ACHIEV': (400, 'This challenge does not have an associated achievement on http://www.usmgames.cl/'),
    'INVALID_HEADER': (400, 'Invalid header'),
    'NEEDS_LOGIN': (401, 'You must be logged in'),
    'PERMISSION_NEEDED': (403, 'You do not have permission to access this resource'),
    'INVALID_TOKEN': (403, 'Invalid token'),
    'NOT_FOUND': (404, 'This resource could not be found'),
    'DELETED_FROM_WP': (404, 'This resource has been deleted from http://www.usmgames.cl/'),
    'NOT_FOUND_ID': (404, 'A resource with this id could not be found'),
    'WORDPRESS_ERROR': (500, 'Could not access to http://www.usmgames.cl/')
}


def throw_error(code: str, custom_message: str = None):
    status_code, message = errors[code]
    if custom_message is not None:
        message = custom_message

    res = jsonify({
        'code': code,
        'message': message
    })
    res.status_code = status_code
    return res
