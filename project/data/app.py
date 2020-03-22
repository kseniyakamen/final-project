from func import *
from flask import Flask, jsonify
import sqlite3


def show_tables():
    q = '''
    SELECT
        name,
        type
    FROM sqlite_master
    WHERE type IN ("table","view");
    '''
    return run_query(q)

def run_query(q):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)


DB = "candidates.db"


app = Flask(__name__)

@app.route('/create_db/', methods=['GET'])
def create_db():
    
    df = sql_update_table_creator()
    tables = {"candidates": df}

    with sqlite3.connect(DB) as conn:    
        for name, data in tables.items():
            conn.execute("DROP TABLE IF EXISTS {};".format(name))
            data.to_sql(name,conn,index=False)
    
    dictionary = show_tables().to_dict(orient = "index")
    return jsonify(dictionary)


if __name__ == "__main__": 
    app.run(port = 8080,debug=True)



