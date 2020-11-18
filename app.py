import datetime

from flask import Flask, render_template, redirect, url_for

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = '^;.AS6?(&bvfd98762":.)'


@app.route('/')
@app.route('/entries')
def index():
    entries = models.Entry.select()
    return render_template('index.html', entries=entries)


@app.route('/entries/new', methods=('GET', 'POST'))
def new():
    form = forms.NewEntry()
    if form.validate_on_submit():
        models.Entry.create_entry(
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learned=form.learned.data,
            ressources=form.ressources.data,
        )
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/<int:entry_id>')
def detail(entry_id):
    entry = models.Entry.get_by_id(entry_id)
    return render_template('detail.html', entry=entry)


@app.route('/entries/<int:entry_id>/edit', methods=('GET', 'POST'))
def edit(entry_id):
    form = forms.NewEntry()
    entry = models.Entry.get_by_id(entry_id)
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.date = form.date.data
        entry.time_spent = form.time_spent.data
        entry.learned = form.learned.data
        entry.ressources = form.ressources.data
        entry.save()
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, entry=entry)


@app.route('/entries/<int:entry_id>/delete')
def delete(entry_id):
    try:
        entry = models.Entry.get_by_id(entry_id)
        entry.delete_instance()
        entry.save()
    except models.DoesNotExist:
        pass
    return redirect(url_for('index'))


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
        models.Tag.base_tags('Python', models.Entry.get_by_id(1))
    except ValueError:
        pass    


    app.run(debug=DEBUG, host=HOST, port=PORT)
