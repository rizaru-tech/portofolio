from flask import render_template

from portfolio.public_web import public_web_bp


PAGES = {
    "home": {
        "title": "Home",
        "heading": "Portfolio foundation",
        "summary": "Fondasi multilingual telah siap untuk dikembangkan bertahap.",
    },
    "projects": {
        "title": "Projects",
        "heading": "Projects",
        "summary": "Konten project akan dikelola melalui content domain pada tahap berikutnya.",
    },
    "cv": {
        "title": "CV",
        "heading": "CV",
        "summary": "Pengelolaan dan download CV belum diimplementasikan pada fondasi ini.",
    },
    "blog": {
        "title": "Blog",
        "heading": "Blog",
        "summary": "Daftar dan detail Blog akan ditambahkan setelah fondasi stabil.",
    },
}


@public_web_bp.get("/")
def home():
    return _render_page("home")


@public_web_bp.get("/projects")
def projects():
    return _render_page("projects")


@public_web_bp.get("/cv")
def cv():
    return _render_page("cv")


@public_web_bp.get("/blog")
def blog():
    return _render_page("blog")


def _render_page(page_name: str):
    return render_template("public/page.html", page=PAGES[page_name])
