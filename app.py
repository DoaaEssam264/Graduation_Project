from flask import Flask, render_template, request, url_for, redirect ,session,flash,jsonify
from database import load_homepage_random_recommendations,load_search_results,add_user,load_user,get_cleaned_categories,get_pages_of_a_certain_category,get_favorite_posts,add_post_to_favorites,number_of_fav_posts,remove_post,show_product_func,generate_gemini_response,upsert_favTable
from flask_bcrypt import Bcrypt
import os
import re



app = Flask(__name__)
bcrypt = Bcrypt(app)
my_secret = os.environ['SECRET_KEY']
app.secret_key = my_secret

#email_regex = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@app.route('/process', methods=['POST'])
def process():
    if 'loggedin' in session:
        data = request.get_json()
        text = data.get('text', '')
        ans = generate_gemini_response(text)
        return jsonify({'response': ans})
    else:
        return jsonify({'response': 'Please login first to be able to use InstaSearch Chatbot'})

@app.route("/favorite", methods=['GET', 'POST'])
def favorite():
    if 'loggedin' in session:
        cleaned_categories = get_cleaned_categories()
        log_username=session['username']
        favorite_posts = get_favorite_posts(log_username)
        return render_template('Favorite.html', categories=cleaned_categories, favorite_posts=favorite_posts)
    return redirect(url_for('register'))

@app.route("/favorite/<post_id>")
def favorite_addtolist(post_id):
    if 'loggedin' in session:
        log_username=session['username']
        add_post_to_favorites(log_username, post_id)
    return redirect(url_for('favorite'))

@app.route("/accountpage")
def accountpage():
    if 'loggedin' in session:
        cleaned_categories = get_cleaned_categories()
        username=session['username']
        NoFavoritePost=number_of_fav_posts(username)
        return render_template('account.html',categories=cleaned_categories,username=username,NoFavoritePost=NoFavoritePost)
    return  redirect(url_for('register'))

@app.route("/")
def home_page():
    pages=load_homepage_random_recommendations()
    cleaned_categories = get_cleaned_categories()
    return render_template('Home.html', recommendations=pages,categories=cleaned_categories)


@app.route("/register", methods=['GET','POST'])
def register():
 
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'register':  # Handle sign-up form submission
            username = request.form.get('register_username')
            email = request.form.get('register_email')
            password = request.form.get('register_password')
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            check = load_user(username)
            if check:
                flash('* Username already exists!', 'error_register')
                return render_template('signup_login.html',form_type='register')                
            else:
                add_user(username, email, hashed_password)
                return redirect(url_for('home_page'))

        elif form_type == 'login':  # Handle sign-in form submission
            username = request.form.get('login_username')
            password = request.form.get('login_password')
            check = load_user(username)
            if check:
                if bcrypt.check_password_hash(check[1], password):
                    session['loggedin'] = True
                    session['username'] = username
                    return redirect(url_for('home_page'))
                else:
                    flash('* Incorrect password!', 'error_login')
                    return redirect(url_for('register'))
            else:
                flash('* Username not found!', 'error_login')
                return redirect(url_for('register'))

    return render_template('signup_login.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('username', None)
   return redirect(url_for('register'))


@app.route("/category/<category>")
def category(category):
    cleaned_categories = get_cleaned_categories()
    category_pages=get_pages_of_a_certain_category(category.lower())
    return render_template('Category_search.html',categories=cleaned_categories,category_pages=category_pages,category_name=category)

@app.route("/search_result")
def search_results():
    data =request.args
    # data =request.form
    cleaned_categories = get_cleaned_categories()
    posts=load_search_results(data['user_input_to_search_bar'])
    #if loggedin: sa3etha hoty fel table el serch bta3o
    dict_len=len(posts)
    return render_template('Product_Search.html', posts=posts,categories=cleaned_categories,dict_len=dict_len)

@app.route("/remove_post/<post_id>")
def remove_fav_post(post_id):
    if 'loggedin' in session:
        log_username=session['username']
        remove_post(log_username, post_id)
    return redirect(url_for('favorite'))

@app.route("/show_product/<post_id>")
def show_product(post_id):
    cleaned_categories = get_cleaned_categories()
    post,str_id=show_product_func(post_id)
    return render_template('SHOW_product.html',
        categories=cleaned_categories,post=post,str_id=str_id)

@app.route('/rate', methods=['POST'])
def rate():
    data = request.get_json()
    rating = int(data.get('rating'))
    print(rating)
    post_id = data.get('post_id')
    page_name = data.get('page_name')
    print(page_name)

    if rating and post_id and 'loggedin' in session :
        log_username = session['username']
        upsert_favTable(log_username, post_id, rating, page_name)
        return jsonify({'response': 'Thank you for rating'})
    else:
        return jsonify({'response': 'Please login first to rate'})

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)