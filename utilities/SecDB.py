from sqlalchemy import create_engine, Column, String, Integer, update, delete, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from baselogger import application_path
import os

Base = declarative_base()


class PyDB(Base):
    """
    Class object defining secrets table
    """

    __tablename__ = 'secrets'

    id = Column('id', Integer, primary_key=True)
    secret = Column('secret', String, unique=True, nullable=False)
    username = Column('username', String, nullable=False)
    password = Column('password', String, nullable=False)


class DB(PyDB):
    """
    Class to perform CRUD functionality with SQLite database
    """
    def __init__(self):
        super().__init__()
        db = os.path.join(application_path, 'secrets.db')
        self.engine = create_engine('sqlite:///' + db)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def create_secrets(self, secret: str, username: str, password: str):
        """
        Create entry in database
        :param secret: String representing secret name for database
        :param username: encrypted username
        :param password:  encrypted password
        :return: None
        """
        db = PyDB()
        db.secret = secret
        db.username = username
        db.password = password
        self.session.add(db)
        self.session.commit()

    def retrieve_secrets(self, secret: str):
        """
        Retrieve entry from database
        :param secret: String secret name
        :return: tuple of encrypted username/password
        """
        stmt = select(PyDB.username, PyDB.password).where(PyDB.secret == secret)
        _results = self.session.execute(stmt)
        return _results

    def update_secret(self, secret: str, username: str or None, password: str):
        """
        Update database entries
        :param secret: string
        :param username: bytes
        :param password: bytes
        :return: None
        """
        if username:
            stmt = update(PyDB).where(PyDB.secret == secret).values(username=username, password=password)
        else:
            stmt = update(PyDB).where(PyDB.secret == secret).values(password=password)
        self.session.execute(stmt)
        self.session.commit()

    def delete_secret(self, secret: str):
        """
        Remove secret from database
        :param secret: string
        :return: None
        """
        stmt = delete(PyDB).where(PyDB.secret == secret)
        self.session.execute(stmt)
        self.session.commit()

    def secret_exists(self, secret: str) -> bool:
        """
        Checks for existence of secret in database
        :param secret: String
        :return: bool
        """
        stmt = select(PyDB.secret).where(PyDB.secret == secret)
        _results = self.session.execute(stmt).first()
        if not _results:
            return False
        else:
            return True
