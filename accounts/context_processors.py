"""
Global Context Processor for MongoDB User Session and Application Meta
"""
def auth_context(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    email = request.session.get('email')
    role = request.session.get('role', 'USER')

    is_authenticated = bool(user_id)
    is_admin = (role == 'ADMIN')

    return {
        'current_user': {
            'id': user_id,
            'username': username,
            'email': email,
            'role': role
        } if is_authenticated else None,
        'is_authenticated': is_authenticated,
        'is_admin': is_admin,
        'user_role': role,
        'app_name': 'AI-Powered Environmental Monitoring Network',
        'current_path': request.path
    }
