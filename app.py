from flask import Flask, render_template, request
import os
import numpy as np
from database import load_homepage_random_recommendations,load_search_results
from database import get_cleaned_categories,get_pages_of_a_certain_category

app = Flask(__name__)

# class User(UserMixin):
#     def __init__(self, id, username, email, password):
#         self.id = id
#         self.username = username
#         self.email = email
#         self.password = password

# metadata = MetaData()
# user_info = Table('user_info', metadata, autoload=True, autoload_with=engine)
# Session = sessionmaker(bind=engine)
# session = Session()
#homepage
#if list of search empty, return random otherwise return pages similars to search

@app.route("/")
def home_page():
    pages=load_homepage_random_recommendations()
    cleaned_categories = get_cleaned_categories()
    return render_template('Home.html', recommendations=pages,categories=cleaned_categories)

# @app.route("/login", methods=['GET','POST'])
# def sign():
#     if request.method=='POST':
#         username=request.form('Username')
#         password=request.form('Password')
#     return render_template('signup_login.html')

@app.route("/category/<category>")
def category(category):
    cleaned_categories = get_cleaned_categories()
    category_pages=get_pages_of_a_certain_category(category.lower())
    return render_template('Category_search.html',categories=cleaned_categories,category_pages=category_pages)



 # cleaned_categories = get_cleaned_categories()
 # category_pages=get_pages_of_a_certain_category(category)
 # return render_template('Category_search.html',categories=cleaned_categories)
    

@app.route("/favorite")
def favorite():
    cleaned_categories = get_cleaned_categories()
    return render_template('Favorite.html',categories=cleaned_categories)

@app.route("/product_info")
def product_info():
    cleaned_categories = get_cleaned_categories()
    return render_template('SHOW_product.html',categories=cleaned_categories)


@app.route("/search_result")
def search_results():
    data =request.args
    # data =request.form
    cleaned_categories = get_cleaned_categories()
    posts=load_search_results(data['user_input_to_search_bar'])
    dict_len=len(posts)
    return render_template('Product_Search.html', posts=posts,categories=cleaned_categories,dict_len=dict_len)
# @app.route("/product_info")
# def product_info():
#     pages=load_homepage_random_recommendations()
#     # unique_categories=get_unique_categories()
#     return render_template('Home.html', recommendations=pages)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

# Access all tables from the reflected metadata
