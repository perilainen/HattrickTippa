import sqlite3
import databasesetting
import os.path

conn = sqlite3.connect(databasesetting.db_path)
curr = conn.cursor()

curr.execute("""DROP TABLE matches;""")


sql_command = """
CREATE TABLE matches (
matchID VARCHAR(20),
homeTeam VARCHAR(50),
AwayTeam VARCHAR(50),
MatchDate VARCHAR(20),
result VARCHAR(20),
MatchRound VARCHAR(20));"""

curr.execute(sql_command)

conn.commit()

conn.close()