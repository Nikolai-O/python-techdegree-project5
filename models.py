import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, password):
        try:
            cls.create(
                username=username,
                password=generate_password_hash(password)
            )
        except IntegrityError:
            raise ValueError("User already exists")


class Entry(Model):
    title = CharField(unique=True)
    date = DateTimeField(default=datetime.datetime.now)
    time_spent = IntegerField()
    learned = TextField()
    ressources = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-date',)

    @classmethod
    def create_entry(cls, title, date, time_spent, learned, ressources):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    date=date,
                    time_spent=time_spent,
                    learned=learned,
                    ressources=ressources
                )
        except IntegrityError:
            raise ValueError("Journal entry already exists.")

    @classmethod
    def base_entry(cls, title, time_spent, learned, ressources):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    time_spent=time_spent,
                    learned=learned,
                    ressources=ressources,
                )
        except IntegrityError:
            raise ValueError("Journal entry already exists.")

    def get_tags(self):
        return Tag.select().where(Tag.entry == self)

    def tagged(self):
        """The tags that this entry has"""
        return(
            Tag.select().join(
                EntryTag,
                on=EntryTag.to_tag).where(EntryTag.from_entry == self)
            )

    def tagged_entry(self):
        """The entries that have this tag"""
        return(
            Entry.select().join(
                EntryTag,
                on=EntryTag.from_entry).where(EntryTag.to_tag == self)
            )


class Tag(Model):
    tag = TextField(unique=True)

    def tagged_entry(self):
        """The entries that have this tag"""
        return(
            Entry.select().join(
                EntryTag,
                on=EntryTag.from_entry).where(EntryTag.to_tag == self)
            )

    class Meta:
        database = DATABASE

    @classmethod
    def base_tags(cls, tag):
        try:
            with DATABASE.transaction():
                cls.create(
                    tag=tag,
                )
        except IntegrityError:
            raise ValueError("Jounral tag already exists.")


class EntryTag(Model):
    from_entry = ForeignKeyField(Entry)
    to_tag = ForeignKeyField(Tag)

    class Meta:
        database = DATABASE
        indexes = (
            (('from_entry', 'to_tag'), True),
        )

    @classmethod
    def base_tags_relation(cls, entry, tag):
        try:
            with DATABASE.transaction():
                cls.create(from_entry=entry, to_tag=tag)
        except IntegrityError:
            raise ValueError("Relation tag already exists.")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry, Tag, EntryTag], safe=True)
    DATABASE.close()
