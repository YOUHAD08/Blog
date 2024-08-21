from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, CommentForm, CreatePostForm


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login
login_manager=LoginManager()
login_manager.login_ivew='get_all_posts'
login_manager.login_message_category='info'
login_manager.init_app(app)



# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Create An Avatare

gravatar = Gravatar(
    app,
    size=100,  # Default size for avatars
    rating='g',  # Image rating ('g', 'pg', 'r', 'x')
    default='wavatar',  # Default avatar type when no avatar is found
    force_default=False,  # Force default image
    force_lower=False,  # Force lower case email addresses
    use_ssl=True,  # Use SSL (https) for avatar URLs
    base_url=None  # Custom base URL for Gravatar avatars
)

# Create a User table for all your registered users. 

class User(db.Model, UserMixin):
    __tablename__ ='user'
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    name : Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(250),unique=True,  nullable=False)
    password : Mapped[str] = mapped_column(String(250),unique=True, nullable=False)
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="author")
    comments : Mapped[list["Comment"]] = relationship(back_populates="user")
# Create Post table contain all posts 
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped[User] = relationship(back_populates="posts")
    blog_post_comments :Mapped[list["Comment"]] = relationship(back_populates="blogpost")

# Create a Comment table to store the comment of the users
class Comment(db.Model):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    
    user: Mapped[User]= relationship(back_populates="comments")
    blogpost: Mapped[BlogPost]= relationship(back_populates="blog_post_comments")
    
    user_id : Mapped[int] = mapped_column(ForeignKey("user.id"))
    blogpost_id : Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


with app.app_context():
    db.create_all()


# TODO: Use Werkzeug to hash the user's password when creating a new user.
n=32768
r=8
p=1
method=f"scrypt:{n}:{r}:{p}"
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You Already Logged In")
        return redirect(url_for("get_all_posts"))
    else: 
        Form=RegisterForm()
        if Form.validate_on_submit():
            name=Form.name.data
            email=Form.email.data
            password=generate_password_hash(Form.password.data, method=method, salt_length=8)
            if User.query.filter_by(name=name).first():
                flash("This User Name is Already Used, Try a Diffrent One")
            elif User.query.filter_by(email=email).first():
                flash("This Email is Already Used, Try a Diffrent One")
            elif User.query.filter_by(password=password).first():
                flash("This Email is Already Used, Try a Diffrent One")
            else: 
                new_user=User(
                    name=name,
                    email=email,
                    password=password
                )
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("login"))
        return render_template("register.html", form=Form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You Already Logged In")
        return redirect(url_for("get_all_posts"))
    else:
        form=LoginForm()
        if form.validate_on_submit():
            user=User.query.filter_by(email=form.email.data).first()
            if user : 
                if check_password_hash(user.password,form.password.data):
                    login_user(user)
                    return redirect(url_for('get_all_posts'))
                else : 
                    flash('The Password is Incorrect, Try Again ')
            else:
                flash('The Email is Incorrect, Try Again')
        return render_template("login.html", form=form)

#admin_only decorator 
def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not(current_user.is_authenticated  and current_user.id == 1) :
            return abort(403)
        return function(*args, **kwargs)
    return wrapper
        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    form=CommentForm()
    if form.validate_on_submit() :
        if current_user.is_authenticated :
            new_comment=Comment(
                comment=form.comment.data,
                user_id =current_user.id,
                blogpost_id=post_id
            )
            db.session.add(new_comment)
            db.session.commit()
        else: 
            flash("Try To log In to Submit Your Comment")
            return redirect(url_for('login'))
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post, form=form, gravatar=gravatar)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y"),
            author_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author_id = current_user.id
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
