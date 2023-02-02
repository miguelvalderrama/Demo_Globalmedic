import sqlite3
import pandas as pd


def connect_to_db():
    # Connect to the database
    mydb = sqlite3.connect('database.db')
    # Create a cursor
    mycursor = mydb.cursor()
    # Return the cursor and the connection
    return mycursor, mydb

''' INSERTAR FORMA #2 PRODUCTOS POR DESCRIPCION
    INSERT INTO (DESCRIPCION, COSTO, DROGUERIA)
    VALUES (DESCRIPCION, COSTO, DROGUERIA)
    .SCHEMA TABLE(DESCRIPCION, COSTO. DROGUERIA)'''
def update_products_wt_description():
    # Open final_csv.csv
    df = pd.read_csv('./temp/final_csv.csv')
    query = '''INSERT INTO visualizador_precios_drogueria_descripcion (descripcion, costo, drogueria)
                VALUES (?, ?, ?)'''
    values = []
    for idx, row in df.iterrows():
        values.append((row['Descripcion'], row['Precio'], row['Proveedor']))
    cursor, conn = connect_to_db()
    cursor.execute("DELETE FROM visualizador_precios_drogueria_descripcion")
    conn.commit()
    cursor.executemany(query, values)
    conn.commit()
    conn.close()

# ================ CREAR TABLAS =======================
# FORMA #2
query_2 = '''CREATE TABLE IF NOT EXISTS visualizador_precios_drogueria_descripcion (
                descripcion VARCHAR(255) NOT NULL, 
                costo FLOAT NOT NULL, 
                drogueria VARCHAR(255) NOT NULL)'''

def create_table(query):
    cursor, db = connect_to_db()
    cursor.execute(query)
    db.commit()
    db.close()
