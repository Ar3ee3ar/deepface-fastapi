import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="test1234",
  database="pic",
  port = 3306
)