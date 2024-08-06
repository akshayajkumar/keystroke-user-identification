import sqlite3 as sql

def create_db():
    try:
        conn = sql.connect('database.db')
        conn.execute('CREATE TABLE tb_usuario (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
        print("INFO - DATABASE - Table created correctly")
        conn.close()
    except:
        print("ERROR - DATABASE - Connection cannot be successful")

def drop_db():
    try:
        conn = sql.connect('database.db')
        conn.execute('DROP TABLE tb_usuario')
        print("INFO - DATABASE - Table deleted successfully!")
        conn.close()
    except:
        print("ERROR - DATABASE - Connection denied or does not exist")

def add_user_and_passw(username, password):
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM tb_usuario WHERE username=?", [username])
            con.row_factory = sql.Row
            rows = cur.fetchall()
            if rows:
                print("Username already exists!")
                return 0, False
            else:
                cur.execute("INSERT INTO tb_usuario (username, password) VALUES (?, ?)", (username, password))
                con.commit()
                user_id = cur.lastrowid
                print("User registered, ID:", user_id)
                return user_id, True
    except:
        print("Error in registration")

def check_user_and_passw(username, password):
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM tb_usuario WHERE username=?", [username])
            con.row_factory = sql.Row
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    user_id = row[0]
                    user = row[1]
                    password_db = row[2]
                if password_db == password:
                    print('WARNING - DATABASE - check_user_and_pass: Username and password match, authenticated user! USER_ID:', user_id, 'USER_NAME:', user)
                    return 2, True, user_id
                else: 
                    print('WARNING - DATABASE - check_user_and_pass: Existing user but password does not match! USER_ID:', user_id, 'USER_NAME:', user)
                    return 1, False, user_id
            else:
                print("ERROR - DATABASE - check_user_and_pass: User does not exist in the database!")
                return 3, False, 0
    except:
        print("ERROR - DATABASE - Unable to verify username and password")

def get_user_and_passw(id):
    try:
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM tb_usuario")
   
        rows = cur.fetchall()
        username = rows[id]['username']
        password = rows[id]['password']
        return username, password
    except:
        print("Unable to retrieve users!")

def get_user_id(username):
    try:
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM tb_usuario WHERE username=?", (username,))
    
        rows = cur.fetchall()
        if rows:
            for row in rows:
                user_id = row[0]
        return user_id
    except:
        print("Unable to obtain USER_ID from database!")
