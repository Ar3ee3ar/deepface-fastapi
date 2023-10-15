import os
from os.path import join, dirname
import mysql.connector
from dotenv import load_dotenv

def filter(start_dt,end_dt):
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    mydb = mysql.connector.connect(
        host = os.environ.get('HOST_db'),
        user=os.environ.get('USER_db'),
        password=os.environ.get('PASSWORD_db'),
        database=os.environ.get('DATABASE_db'),
        port = os.environ.get('PORT_db')
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id,pic_path, create_time FROM kiosk_robot_snap WHERE create_time BETWEEN '"+start_dt+"' AND '"+end_dt+"' order by create_time")
    myresult = mycursor.fetchall()
    return myresult

def get_all():
    # date format y/m/d
    # start_dt = 2008-01-01 00:00:00
    # end_dt = 2008-01-10 00:00:00
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    mydb = mysql.connector.connect(
        host = os.environ.get('HOST_db'),
        user=os.environ.get('USER_db'),
        password=os.environ.get('PASSWORD_db'),
        database=os.environ.get('DATABASE_db'),
        port = os.environ.get('PORT_db')
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id,pic_path, create_time FROM kiosk_robot_snap order by create_time")
    myresult = mycursor.fetchall()
    return myresult