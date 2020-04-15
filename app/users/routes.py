
from flask import url_for, render_template, flash, redirect, request, abort, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db , bcrypt
from app.models import User, Post
from app.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                        RequestResetForm, ResetPasswordForm)
from app.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register/", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        #so that the user can't login more than once after first login 
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username= form.username.data, email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully,you can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template("register.html", title="Register", form = form)


@users.route("/login/", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Logged in {user.username} successfully', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
            #redirect to next page if next page exists else redirect to home page
        else:
            flash('Login was unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", title="Login", form = form)


@users.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/profile/', methods=['GET','POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file= picture_file
        current_user.username= form.username.data
        current_user.email= form.email.data
        db.session.commit()
        flash('your account has been updated!', 'success')
        return redirect(url_for('users.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_photo/' + current_user.image_file)
    return render_template("profile.html", title="Profile",
                            image_file=image_file, form=form)


@users.route("/user/<string:username>/")
def user_posts(username):
    page = request.args.get('page', 1 , type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=4)
    return render_template("user_posts.html", user=user, title="blogposts", posts=posts)


@users.route("/reset_password/", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.','info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password was updated successfully', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)