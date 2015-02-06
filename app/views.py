from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, ChannelForm, PostForm
from models import User, Channel, Post
from utility import calculate_text
from ycombinator import Ycombinator


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

    
@app.before_request
def before_request():
    g.user = current_user

    
@app.route('/')
@app.route('/index')
@login_required
def index():	
    return render_template('index.html',
        title = 'Home',
        user = g.user)


@app.route('/search', methods = ['GET', 'POST'])
@login_required
def search():
    form = ChannelForm(request.form)
    if request.method == "POST"  and form.validate():
        channels = Channel.query.filter(Channel.name.like(
            '%' + form.name.data + '%' ))
    else:
        channels = Channel.query.all()
    return render_template('search.html',
        channels=channels,
        form = form,
    	title = 'Search channels',
        user = g.user)


@app.route('/channel/add', methods = ['POST', 'GET'])
@login_required
def add_channel():
    form = ChannelForm(request.form)
    if request.method == 'POST' and form.validate():
        channel = Channel(name = form.name.data)
        channel.owner_id = g.user.id
        db.session.add(channel)
        db.session.commit()
        return redirect(url_for('channel_view', id=channel.id))
    return render_template('add_channel.html',
        title = 'Add channel',
        user = g.user,
        form = form)


@app.route('/channel/<int:id>')
@login_required
def channel_view(id):
    channel = Channel.query.filter_by(id=id).first_or_404()
    return render_template('channel_view.html',
        title = 'Channel %s' % channel.name,
        channel = channel,
        user_in_chat = g.user in channel.users.all(), 
        form = PostForm(),
        user = g.user)


@app.route('/channel/posts/<int:channel>')
@login_required
def channel_posts(channel):
    return render_template('post_list.html',
        posts=Channel.query.filter_by(id=channel).first_or_404().posts.all(),
        user = g.user)


@app.route('/channel/add_news/<int:channel>')
@login_required
def check_ycombinator_posts(channel):
    Ycombinator().add_news(channel)
    return jsonify(result=1)

        
@app.route('/post/add/<int:channel>', methods = ['POST'])
@login_required
def add_post(channel):
    form = PostForm(request.form)
    if form.validate():
        post = Post(body = calculate_text(form.body.data))
        post.user_id = g.user.id
        post.channel_id = channel
        db.session.add(post)
        db.session.commit()
    return jsonify(result=1)


@app.route('/user/add/<int:channel_id>')
@login_required
def add_user(channel_id):
    Channel.query.filter_by(id=channel_id).first_or_404().users.append(g.user)
    db.session.commit()
    return redirect(url_for('channel_view', id=channel_id))


@app.route('/user/remove/<int:channel_id>')
@login_required
def remove_user(channel_id):
    Channel.query.filter_by(id=channel_id).first_or_404().remove_user(g.user)
    return redirect(url_for('channel_view', id=channel_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("Wrong username or password")
            return render_template("login.html", form=form)
        if not user.check_password(form.password.data):
            flash("Wrong password")
            return render_template("login.html", form=form)
        login_user(user)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).count():
            flash("Username '%s' is busy. Please choose another.")
            return render_template("login.html", form=form)
        user = User(form.username.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Logged in successfully.")
        return redirect(url_for("index"))
    return render_template("register.html", form=form)

    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
