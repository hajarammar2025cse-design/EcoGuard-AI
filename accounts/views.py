"""
Accounts Views: Authentication, Profile, and User Management
"""
from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password, check_password

from config.db import get_users_col, serialize_docs, serialize_doc, check_db_connection
from accounts.auth_helper import (
    create_user, authenticate_user, login_required_custom, admin_required_custom, get_user_by_id
)

def login_view(request):
    # Check DB connection
    db_ok, db_msg = check_db_connection()
    if not db_ok:
        messages.error(request, f"Database Connection Warning: {db_msg}")

    if request.session.get('user_id'):
        return redirect('/dashboard/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', False)

        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, 'accounts/login.html', {'username': username})

        user = authenticate_user(username, password)
        if user:
            # Set session
            request.session['user_id'] = user['id']
            request.session['username'] = user['username']
            request.session['email'] = user.get('email', '')
            request.session['role'] = user.get('role', 'USER')

            if remember:
                request.session.set_expiry(86400 * 14)  # 14 days
            else:
                request.session.set_expiry(86400)      # 1 day

            messages.success(request, f"Welcome back, {user['username'].capitalize()}! Logged in as {user['role']}.")
            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('/dashboard/')
        else:
            messages.error(request, "Invalid username or password, or account is disabled.")

    return render(request, 'accounts/login.html')

def register_view(request):
    if request.session.get('user_id'):
        return redirect('/dashboard/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validations
        if not username or not email or not password:
            messages.error(request, "All required fields must be filled.")
            return render(request, 'accounts/register.html', {'username': username, 'email': email})

        if len(username) < 3:
            messages.error(request, "Username must be at least 3 characters.")
            return render(request, 'accounts/register.html', {'username': username, 'email': email})

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return render(request, 'accounts/register.html', {'username': username, 'email': email})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html', {'username': username, 'email': email})

        success, res = create_user(username, email, password, role="USER")
        if success:
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('/accounts/login/')
        else:
            messages.error(request, res)

    return render(request, 'accounts/register.html')

def logout_view(request):
    username = request.session.get('username', 'User')
    request.session.flush()
    messages.info(request, f"Goodbye {username.capitalize()}, you have been logged out.")
    return redirect('/')

@login_required_custom
def profile_view(request):
    user_id = request.session.get('user_id')
    user = get_user_by_id(user_id)
    if not user:
        request.session.flush()
        return redirect('/accounts/login/')

    if request.method == 'POST':
        action = request.POST.get('action')
        users_col = get_users_col()

        if action == 'update_info':
            new_email = request.POST.get('email', '').strip().lower()
            if new_email:
                users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'email': new_email}})
                request.session['email'] = new_email
                messages.success(request, "Email updated successfully.")

        elif action == 'change_password':
            old_pw = request.POST.get('old_password', '')
            new_pw = request.POST.get('new_password', '')
            confirm_new_pw = request.POST.get('confirm_new_password', '')

            db_user = users_col.find_one({'_id': ObjectId(user_id)})
            if not db_user or not check_password(old_pw, db_user.get('password', '')):
                messages.error(request, "Current password is incorrect.")
            elif len(new_pw) < 6:
                messages.error(request, "New password must be at least 6 characters.")
            elif new_pw != confirm_new_pw:
                messages.error(request, "New passwords do not match.")
            else:
                users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': make_password(new_pw)}})
                messages.success(request, "Password changed successfully.")

        user = get_user_by_id(user_id)

    return render(request, 'accounts/profile.html', {'user': user})

@admin_required_custom
def user_management_view(request):
    users_col = get_users_col()
    users_cursor = users_col.find().sort('created_at', -1)
    users = serialize_docs(users_cursor)
    return render(request, 'accounts/user_management.html', {'users': users})

@admin_required_custom
@require_http_methods(["POST"])
def toggle_user_role(request, user_id):
    users_col = get_users_col()
    try:
        user = users_col.find_one({'_id': ObjectId(user_id)})
        if not user:
            messages.error(request, "User not found.")
            return redirect('/accounts/users/')

        # Prevent admin from demoting self
        if str(user['_id']) == request.session.get('user_id'):
            messages.warning(request, "You cannot modify your own administrator role.")
            return redirect('/accounts/users/')

        new_role = 'USER' if user.get('role') == 'ADMIN' else 'ADMIN'
        users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})
        messages.success(request, f"User '{user.get('username')}' role updated to {new_role}.")
    except Exception as e:
        messages.error(request, f"Error updating role: {e}")

    return redirect('/accounts/users/')

@admin_required_custom
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    users_col = get_users_col()
    try:
        user = users_col.find_one({'_id': ObjectId(user_id)})
        if not user:
            messages.error(request, "User not found.")
            return redirect('/accounts/users/')

        if str(user['_id']) == request.session.get('user_id'):
            messages.warning(request, "You cannot disable your own active administrator account.")
            return redirect('/accounts/users/')

        new_status = not user.get('is_active', True)
        users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_active': new_status}})
        status_label = "activated" if new_status else "disabled"
        messages.success(request, f"User '{user.get('username')}' account {status_label}.")
    except Exception as e:
        messages.error(request, f"Error updating account status: {e}")

    return redirect('/accounts/users/')
