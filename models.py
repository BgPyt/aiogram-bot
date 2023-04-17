from peewee import *
import os
from dotenv import load_dotenv

load_dotenv()

db = PostgresqlDatabase(os.environ['DB_USER'],
                        user=os.environ['DB_USER'],
                        password=os.environ['DB_PASSWORD'],
                        host='db',
                        port='5432',
                        )


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    class Meta:
        db_table = 'Users'

    user_id = IntegerField()
    first_name = CharField(null=True)
    username = CharField()
    date = DateTimeField()
    is_bot = BooleanField()
    language_code = CharField()

    def __str__(self):
        return self.user_id


class Filter_Vacancy(BaseModel):
    class Meta:
        db_table = 'Filters'

    name = CharField(null=True)
    income = CharField(null=True)
    schedule = CharField(null=True)
    experience = CharField(null=True)
    user = ForeignKeyField(User, related_name='FILTER', on_delete='CASCADE')


try:
    if __name__ == '__main__':
        db.create_tables([User, Filter_Vacancy])
except:
    pass

