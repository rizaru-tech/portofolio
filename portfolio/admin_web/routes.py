from flask import render_template

from portfolio.admin_web import admin_web_bp


@admin_web_bp.get("")
@admin_web_bp.get("/")
def index():
    return render_template("admin/index.html")
