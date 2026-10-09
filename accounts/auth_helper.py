"""
Authentication and Authorization Helper Layer
Interfaces with MongoDB 'users' collection using Django's secure password hashers.
"""
from datetime import datetime
from functools import wraps
from bson import ObjectId
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from config.db import get_users_col, serialize_doc

def create_user(username, email, password, role="USER"):
    """
    Creates a new user in MongoDB with safely hashed password.
    Returns (success: bool, user_doc_or_error: dict|str)
    """
    users_col = get_users_col()
    username = username.strip().lower()
    email = email.strip().lower()

    if users_col.find_one({"username": username}):
        return False, "Username already exists. Please choose another."
    
    if users_col.find_one({"email": email}):
        return False, "Email address already registered."

    hashed_pw = make_password(password)
    user_doc = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "role": role.upper(),  # 'ADMIN' or 'USER'
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    result = users_col.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return True, serialize_doc(user_doc)

def authenticate_user(username, password):
    """
    Validates user credentials against MongoDB record.
    Returns serialized user dict if valid, else None.
    """
    users_col = get_users_col()
    username = username.strip().lower()
    user = users_col.find_one({"username": username})
    if not user:
        return None
    
    if not user.get("is_active", True):
        return None

    if check_password(password, user.get("password", "")):
        return serialize_doc(user)
    return None

def get_user_by_id(user_id):
    users_col = get_users_col()
    try:
        user = users_col.find_one({"_id": ObjectId(user_id)})
        return serialize_doc(user)
    except Exception:
        return None

def login_required_custom(view_func):
    """
    Decorator requiring active MongoDB authenticated session.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, "Please log in to access this page.")
            return redirect(f"/accounts/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required_custom(view_func):
    """
    Decorator requiring ADMIN role privileges.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, "Please log in with administrator privileges.")
            return redirect(f"/accounts/login/?next={request.path}")
        
        role = request.session.get('role', 'USER')
        if role != 'ADMIN':
            messages.error(request, "Access Denied: Administrator role required.")
            return redirect('/dashboard/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
