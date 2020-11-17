import datetime

from peewee import *

DATABASE = SqliteDatabase('journal.db')

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
                    ressources=ressources
                )
        except IntegrityError:
            raise ValueError("Journal entry already exists.")

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Entry], safe=True)
    DATABASE.close()
