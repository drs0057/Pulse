import mysql.connector
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
engine = create_engine('mysql+mysqlconnector://tigers0057:0L85Z4IkBslEP5T3MMjp@musicdb.c8wcmnsrregt.us-east-2.rds.amazonaws.com:3306/music')
Session = sessionmaker(bind=engine, autocommit=False, autoflush=True)

session = Session()
session.execute(text("INSERT INTO users (username, password) VALUES ('test1', 'test1')"))
session.commit()
result = session.execute(text("SELECT * FROM users"))
for row in result:
    print(row)
session.close()
