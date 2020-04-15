
from flask import render_template, request, Blueprint
from app.models import Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home/")
def home():
    return render_template("home.html", title="home")


@main.route("/about/")
def about():
    return render_template("about.html", title="about")


@main.route("/services/")
def services():
    return render_template("services.html", title="services")


@main.route("/blog/")
def blog():
    page = request.args.get('page', 1 , type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template("blog.html", title="blogposts",posts=posts)


@main.route("/team/")
def team():
    return render_template("team.html", title="team members")