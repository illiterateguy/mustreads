import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                    # DATABASE_URL is an environment variable that indicates where the database lives 
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                    # database are kept separate

db.execute("CREATE TABLE users(user_id SERIAL PRIMARY KEY,username VARCHAR NOT NULL,password VARCHAR NOT NULL,email VARCHAR NOT NULL)")
db.execute("CREATE TABLE books(isbn VARCHAR PRIMARY KEY,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year INTEGER NOT NULL)")
db.execute("CREATE TABLE reviews(isbn VARCHAR REFERENCES books,user_id INT REFERENCES users,rating INT NOT NULL,review VARCHAR NOT NULL,PRIMARY KEY(isbn,user_id))")

