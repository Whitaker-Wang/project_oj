from flask import jsonify, render_template, request

from app.api_1_0 import api


@api.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@api.app_errorhandler(500)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
#
#
# def forbidden(message):
#     response = jsonify({'error': 'forbidden', 'message': message})
#     response.status_code = 403
#     return response
#
#
# def unauthorized(message):
#     return jsonify({'message': message})
