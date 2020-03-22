from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
import sqlite3
import pandas as pd

DB = "data/candidates.db"

def run_query(q):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)
    
def run_command(c):
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.isolation_level = None
        conn.execute(c)

def show_tables():
    q = '''
    SELECT
        name,
        type
    FROM sqlite_master
    WHERE type IN ("table","view");
    '''
    return run_query(q)

def exact_match(key_word):
    q = "SELECT * FROM candidates;"
    df = run_query(q)
    idx = []
    i = 0
    for row in df["keywords"]:
        df.loc[i,"keywords"] = row.split(" ")
        lst = df.loc[i,"keywords"]
        ser = pd.Series(sorted(lst)).drop_duplicates()
        logic = False
        for row in ser:
            row = row.lower()
            row = row.split()
            if row == key_word:
                logic = True
            else:
                pass
        if logic == True:
            idx.append(i)
            i =+ 1
        else:
            i =+ 1
    return df.loc[idx, :]

def partial_match(key_word):
    q = "SELECT * FROM candidates C WHERE C.keywords LIKE '%{}%';".format(key_word)
    return run_query(q)


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/profile', methods=['POST'])
def profile_post():
    keyword = request.form.get('keyword')
    keyword = keyword.lower()
    
    if len(keyword) == 0:
        flash("Please insert a key word!")
        return redirect(url_for('main.profile'))
    
    #Calling Partial Match
    elif request.form.get('check')== "1" and len(keyword) > 0:
        results = partial_match(keyword)
        if len(results) == 0:
            flash("No matching key word found!")
            return redirect(url_for('main.profile'))
        else:
            results = results.drop("keywords", 1)
            return render_template('output.html',  tables=[results.to_html(classes='data')], titles=results.columns.values)
    
    #Calling Exact Match
    elif request.form.get('check') == None and len(keyword) > 0:
        results = exact_match(keyword)
        if len(results) == 0:
            flash("No matching key word found!")
            return redirect(url_for('main.profile'))
        else:
            results = results.drop("keywords", 1)
            return render_template('output.html',  tables=[results.to_html(classes='data')], titles=results.columns.values)
        
    else:
        #flash("There has been an error - Please report to Kseniya Kamenshikh for debugging")
        flash(request.form.get('check'))
        return redirect(url_for('main.profile'))