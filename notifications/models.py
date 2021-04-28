import json
import re
from petrovich.main import Petrovich
from urllib.parse import quote
from petrovich.enums import Case, Gender
import pymysql
from datetime import datetime
from pymysql.cursors import DictCursor
from json import JSONEncoder

_db = pymysql.connect(host="localhost",
                      user="root",
                      password="root",
                      db="data",
                      cursorclass=DictCursor)


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class User:
    def __init__(self, role: int, id: int, fio: str = None):
        self.role = role
        self.id = id
        self.fio = fio
    
    @staticmethod
    def get_user(email_or_id):
        with _db.cursor() as cur:
            cur.execute("SELECT * FROM info_teacher"
                        f" WHERE email = '{email_or_id}'")
            data = cur.fetchone()
            if data is None:
                cur.execute("SELECT * FROM info_students"
                            f" WHERE id_yandex = {email_or_id}")
                data = cur.fetchone()
                if data is None:
                    return None
                id = data["id"]
            else:
                fio = data["fio"]
                id = data["klass_ruk_id"]
            roll = data["roll"]
            return User(roll, id, fio)


class Notification:
    def __init__(self, recivers: list, sender: str, text: str, head: str, _id: int = None):
        self.text = text
        self.head = head
        self.sender = sender
        self._id = _id
        self._recivers = recivers
    
    @property
    def id(self):
        return self._id
    
    @property
    def recivers(self):
        return self._recivers
    
    def save(self):
        with _db.cursor() as cur:
            if self._id is None:
                cur.execute("INSERT INTO news(head, text, sender, publish_date)"
                            f" VALUES ('{self.head}', '{self.text}', '{self.sender}',"
                            f" CAST(N'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' AS DATETIME))")
                _db.commit()
                self._id = cur.lastrowid
                for i in self.recivers:
                    cur.execute("INSERT INTO news_recivers(news_id, reciver)"
                                f" VALUES ({self._id}, '{i}')")
                _db.commit()
            else:
                cur.execute(f"UPDATE news SET"
                            f" text = '{self.text}',"
                            f" head = '{self.head}'"
                            f" WHERE id = {self._id}")
    
    @property
    def gen_name(self):
        lastname, firstname, middlename = self.sender.split()
        lastname = Petrovich().lastname(lastname, Case.GENITIVE).capitalize()
        return lastname + " " \
            + firstname[0].upper() + "." \
            + middlename[0].upper() + "."
    
    @property
    def short_text(self):
        text = re.sub(r"<[^<>]+>", "", self.text)
        dot_index = text.find(".")
        if dot_index == -1:
            return text[:100] + "..."
        return text[:dot_index if dot_index < 100 else 100] + "..."
    
    def to_json(self):
        return {"text": self.text,
                "head": self.head,
                "sender": self.sender,
                "recivers": self._recivers,
                "id": self._id,
                "short_text": self.short_text,
                "sended_from": self.gen_name}
    
    @staticmethod
    def get_by_reciver(reciver: User) -> list:
        with _db.cursor() as cur:
            cur.execute("SELECT * FROM news_recivers"
                        f" WHERE reciver = 'id:{reciver.id}' OR reciver = 'roll:{reciver.role}'")
            news_data = cur.fetchall()
            news = []
            for i in news_data:
                cur.execute(f"SELECT * FROM news WHERE id = {i['news_id']}")
                n_data = cur.fetchone()
                cur.execute(f"SELECT * FROM news_recivers WHERE news_id = {i['news_id']}")
                r_data = cur.fetchall()
                if n_data is None or len(r_data) == 0:
                    continue
                r_data = [j["reciver"] for j in r_data]
                news.append(Notification(r_data, n_data["sender"], n_data["text"],
                                         n_data["head"], n_data["id"]))
            return news
    
    @staticmethod
    def get_by_id(id: int):
        with _db.cursor() as cur:
            cur.execute(f"SELECT * FROM news WHERE id = {id}")
            news = cur.fetchone()
            cur.execute(f"SELECT reciver FROM news_recivers WHERE news_id = {id}")
            recivers = cur.fetchall()
            if len(recivers) == 0 or news is None:
                return None
            recivers = [i["reciver"] for i in recivers]
            return Notification(recivers, news["sender"], news["text"], news["head"], news["id"])
