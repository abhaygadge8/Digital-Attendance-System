from __future__ import annotations

from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from .forms import LoginForm
from .models import Admin


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for("auth.login", next=request.url))
        return view(**kwargs)

    return wrapped_view


@auth_bp.before_app_request
def load_logged_in_admin() -> None:
    admin_id = session.get("admin_id")
    g.admin = Admin.query.get(admin_id) if admin_id else None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.admin:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data.strip()).first()
        if admin and admin.check_password(form.password.data):
            session.clear()
            session["admin_id"] = admin.id
            flash("Login successful.", "success")
            return redirect(request.args.get("next") or url_for("main.dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
