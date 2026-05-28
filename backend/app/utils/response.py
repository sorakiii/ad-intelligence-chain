from flask import jsonify

def success_response(message='success', data=None):
    """成功响应"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)

def error_response(message, code=400):
    """错误响应"""
    return jsonify({
        'success': False,
        'message': message,
        'code': code
    }), code 