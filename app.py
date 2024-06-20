from flask import Flask, render_template, request
import os
import numpy as np
import distutils
from database import load_homepage_random_recommendations,load_search_results,get_cleaned_categories

app = Flask(__name__)

#homepage
#if list of search empty, return random otherwise return pages similars to search
@app.route("/")
def home_page():
    pages=load_homepage_random_recommendations()
    cleaned_categories = get_cleaned_categories()
    return render_template('Home.html', recommendations=pages,categories=cleaned_categories)

@app.route("/sign")
def sign():
    return render_template('signup_login.html')



@app.route("/search_result")
def search_results():
    data =request.args
    # data =request.form
    posts=load_search_results(data['user_input_to_search_bar'])
    return render_template('Product_Search.html', posts=posts)
# @app.route("/product_info")
# def product_info():
#     pages=load_homepage_random_recommendations()
#     # unique_categories=get_unique_categories()
#     return render_template('Home.html', recommendations=pages)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

# Access all tables from the reflected metadata
