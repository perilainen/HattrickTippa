import sqlite3

import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "LID785S61")

conn = sqlite3.connect(db_path)
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