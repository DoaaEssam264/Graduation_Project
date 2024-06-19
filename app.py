from flask import Flask, render_template, request
import os
from database import load_homepage_random_recommendations

app = Flask(__name__)

#homepage
#if list of search empty, return random otherwise return pages similars to search
@app.route("/home")
def home_page():
    pages=load_homepage_random_recommendations()
    # unique_categories=get_unique_categories()
    return render_template('Home.html', recommendations=pages)
    
@app.route("/search_results",methods=['POST'])
def serach_results():
    # data =request.args
     data =request.form
    pages=load_search_results(data['query'])
    # unique_categories=get_unique_categories()
    return render_template('Product_Search.html', recommendations=pages)
# @app.route("/product_info")
# def product_info():
#     pages=load_homepage_random_recommendations()
#     # unique_categories=get_unique_categories()
#     return render_template('Home.html', recommendations=pages)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

# Access all tables from the reflected metadata
