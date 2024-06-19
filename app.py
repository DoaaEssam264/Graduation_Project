from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
import os
from database import load_homepage_random_recommendations

app = Flask(__name__)

# database
db_connecton_uri = os.environ['db_connection_uri']
engine = create_engine(db_connecton_uri)

# @app.route("/")
# def insta_search():
#     return render_template('Home.html')
#TO CHECK DB
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT category FROM pages"))
#     usernamess = [row for row in result.all()]
# print(usernamess)



#homepage
#if list of search empty, return random otherwise return pages similars to search
@app.route("/home")
def home_page():
    pages=load_homepage_random_recommendations()
    # unique_categories=get_unique_categories()
    return render_template('Home.html', recommendations=pages)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

# Access all tables from the reflected metadata
