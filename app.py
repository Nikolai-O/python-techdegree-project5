import datetime

from peewee import *
from flask import Flask, render_template, redirect, url_for, g, flash, abort
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = '^;.AS6?(&bvfd98762":.)'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("Your username or password doesn't match", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your username or password doesn't match", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/entries')
def index():
    entries = models.Entry.select()
    return render_template('index.html', entries=entries)


@app.route('/listing/<int:tag_id>')
def listing(tag_id):
    try:
        tag = models.Tag.get_by_id(tag_id)
    except models.DoesNotExist:
        abort(404)
    return render_template('listing.html', tag=tag)


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new():
    form = forms.NewEntry()
    if form.validate_on_submit():
        tag_list = form.tags.data.split()
        models.Entry.create_entry(
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learned=form.learned.data,
            ressources=form.ressources.data,
        )

        for tag in tag_list:
            if models.DoesNotExist:
                try:
                    models.Tag.create(tag=tag)
                except IntegrityError:
                    pass
                models.EntryTag.base_tags_relation(
                    models.Entry.get(models.Entry.title**form.title.data),
                    models.Tag.get(models.Tag.tag**tag)
                    )
            else:
                models.EntryTag.base_tags_relation(
                    models.Entry.get(models.Entry.title**form.title.data),
                    models.Tag.get(models.Tag.tag**form.tags.data)
                    )

        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/<int:entry_id>')
def detail(entry_id):
    try:
        entry = models.Entry.get_by_id(entry_id)
    except DoesNotExist:
        abort(404)
    return render_template('detail.html', entry=entry)


@app.route('/entries/<int:entry_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(entry_id):
    try:
        entry = models.Entry.get_by_id(entry_id)
    except DoesNotExist:
        abort(404)
    form = forms.NewEntry()
    tags = []
    for tag in models.Entry.get_by_id(entry_id).tagged():
        tags.append(tag.tag)
    tags = ' '.join(tags)
    if form.validate_on_submit():
        tag_list = form.tags.data.split()
        entry.title = form.title.data
        entry.date = form.date.data
        entry.time_spent = form.time_spent.data
        entry.learned = form.learned.data
        entry.ressources = form.ressources.data

        for tag in tags.split(" "):
            if tag not in tag_list:
                models.EntryTag.get(
                    from_entry=models.Entry.get(
                        models.Entry.title**form.title.data),
                    to_tag=models.Tag.get(
                        models.Tag.tag**tag)).delete_instance()

        for tag in tag_list:
            if tag not in models.Entry.get_by_id(entry_id).tagged():
                if models.DoesNotExist:
                    try:
                        models.Tag.create(tag=tag)
                    except IntegrityError:
                        pass
                    try:
                        models.EntryTag.base_tags_relation(
                            models.Entry.get(
                                models.Entry.title**form.title.data),
                            models.Tag.get(models.Tag.tag**tag)
                            )
                    except ValueError:
                        pass

        entry.save()
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, entry=entry, tags=tags)


@app.route('/entries/<int:entry_id>/delete')
@login_required
def delete(entry_id):
    try:
        entry = models.Entry.get_by_id(entry_id)
    except models.DoesNotExist:
        abort(404)
    tags = []
    for tag in entry.tagged():
        tags.append(tag.tag)
    for tag in tags:
        models.EntryTag.get(
            from_entry=models.Entry.get(models.Entry.title**entry.title),
            to_tag=models.Tag.get(models.Tag.tag**tag)).delete_instance()
    entry.delete_instance()
    entry.save()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    try:
        models.Entry.base_entry(
            title='Flask',
            time_spent='8',
            learned='Learned to build apps with Flask',
            ressources='Treehouse'
        )

    except ValueError:
        pass

    try:
        models.Entry.base_entry(
            title='Peewee',
            time_spent='4',
            learned='Learned about Databases through Peewee',
            ressources='Treehouse'
        )
    except ValueError:
        pass

    try:
        models.Entry.base_entry(
            title='Terminal',
            time_spent='1',
            learned='Learned to use the terminal properly',
            ressources='Treehouse'
            )
    except ValueError:
        pass

    try:
        models.Tag.base_tags('Python')
    except ValueError:
        pass

    try:
        models.Tag.base_tags('Operating System')
    except ValueError:
        pass

    try:
        models.EntryTag.base_tags_relation(
            models.Entry.get_by_id(1),
            models.Tag.get_by_id(1)
        )
    except ValueError:
        pass

    try:
        models.EntryTag.base_tags_relation(
            models.Entry.get_by_id(2),
            models.Tag.get_by_id(1)
        )
    except ValueError:
        pass

    try:
        models.EntryTag.base_tags_relation(
            models.Entry.get_by_id(3),
            models.Tag.get_by_id(2)
        )
    except ValueError:
        pass

    try:
        models.User.create_user(
            username='editor',
            password='editentries'
            )
    except ValueError:
        pass

    app.run(debug=DEBUG, host=HOST, port=PORT)
