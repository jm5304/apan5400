import matplotlib
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import numpy as np
import psycopg2, os


conn_url = 'postgresql://postgres:123@localhost/5400'
engine = create_engine(conn_url)
connection = engine.connect()

conn = psycopg2.connect(
    host="localhost",
    port='5432',
    database="5400",
    user="postgres",
    password="123")
cur = conn.cursor()

# from flask import render_template

# from app.forms import SearchForm
# import psycopg2



from flask import Flask, request, render_template
app = Flask("Interactive App")



@app.route('/')
def front_page():
    output = "Hello, please select the service 111"
    return render_template('index.html', result=output)

@app.route('/searchType')
def s_by_Type_index():
    return render_template('searchType.html')

@app.route('/searchType', methods=['POST'])
def s_by_Type_result():
    #Assume database connection has finished
    pop_type ='''
                       SELECT id, title, start_year, average_rating, num_votes, crime
    FROM movies
    WHERE %s=1
    ''' % (request.form.get('mvtype'))###提取name，用这个% 
    cur.execute(pop_type)
    result_df = pd.DataFrame(cur.fetchall(),columns=['id','title','start_year','average_rating','num_votes','crime'])
    return render_template('result_template.html', result=result_df.to_html(header = True))

@app.route('/vote')
def s_by_title_index():
    return render_template('vote.html')

# @app.route('/vote', methods=['GET', 'POST'])
# def home():
#     """Render the home page."""
#     form = SearchForm()
#     search_results = None
#     if form.validate_on_submit():
#         search_term = form.username.data
#         cur = conn.cursor()
#         cur.execute(f"SELECT id,title,average_rating,num_votes FROM movies WHERE num_votes > '{search_term}';")
#         search_results = cur.fetchall()
#         cur.close()
#     return render_template(
#         "vote_result.html", form=form, search_results=search_results)


@app.route('/vote', methods=['POST'])
def s_by_Type_vote():
    #Assume database connection has finished
    num_vote='''
                       SELECT id, title, start_year, average_rating, num_votes, crime
    FROM movies
    WHERE num_votes> %d
    ''' % (request.form.get('vote')) 
    cur.execute(num_vote)
    result_df = pd.DataFrame(cur.fetchall(),columns=['id','title','start_year','average_rating','num_votes'])
    return render_template('vote_result.html', result=result_df.to_html(header = True))




if __name__ == '__main__':
    
    app.run(host='localhost',port=54321)


