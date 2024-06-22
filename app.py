from flask import Flask, render_template, request, url_for, redirect ,session
from database import load_homepage_random_recommendations,load_search_results,add_user,load_user,get_cleaned_categories,get_pages_of_a_certain_category
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
my_secret = os.environ['SECRET_KEY']
app.secret_key = my_secret


@app.route("/favorite")
def favorite():
    if 'loggedin' in session:
        cleaned_categories = get_cleaned_categories()
        return render_template('Favorite.html',categories=cleaned_categories)
    return  redirect(url_for('register'))


# @app.route("/chatbot")
# def chatbot():
#     if 'loggedin' in session:
#         cleaned_categories = get_cleaned_categories()
#         return render_template('Favorite.html',categories=cleaned_categories)
#     return  redirect(url_for('register'))

@app.route("/register", methods=['GET','POST'])
def register(): 
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'register':
            username = request.form.get('register_username')
            email=request.form.get('register_email')
            password = request.form.get('register_password')
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            check=load_user(username)
            if check:
                # Add error message
                return  redirect(url_for('register', error='Username already exists'))
                # return render_template('signup_login.html', form_type=form_type, error='Username already exists')
            else:
                add_user(username, email, hashed_password)
                return redirect(url_for('home_page'))
        elif form_type == 'login':
            username = request.form.get('login_username')
            password = request.form.get('login_password')
            check=load_user(username)
            if check:
                if bcrypt.check_password_hash(check[1], password):
                    # Create session data
                    session['loggedin'] = True
                    session['id'] = session.get('id_counter', 1)
                    session['id_counter'] = session['id'] + 1
                    session['username'] = username
                    return redirect(url_for('home_page'))
                else:
                        return redirect(url_for('register'))
                        #print('user's password wrong')
            else:
                    return redirect(url_for('register'))
                #print('wrong username')
    return render_template('signup_login.html')
        


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('username', None)
   return redirect(url_for('register'))

@app.route("/")
def home_page():
    pages=load_homepage_random_recommendations()
    cleaned_categories = get_cleaned_categories()
    return render_template('Home.html', recommendations=pages,categories=cleaned_categories)

@app.route("/category/<category>")
def category(category):
    cleaned_categories = get_cleaned_categories()
    category_pages=get_pages_of_a_certain_category(category.lower())
    return render_template('Category_search.html',categories=cleaned_categories,category_pages=category_pages,category_name=category)

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
