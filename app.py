from flask import Flask, render_template, request, url_for, redirect ,session,flash,jsonify
import json
import tabulate
import sqlparse
from database import load_homepage_random_recommendations,load_search_results,add_user,load_user,get_cleaned_categories,get_pages_of_a_certain_category,get_favorite_posts,add_post_to_favorites,number_of_fav_posts,remove_post,show_product_func,execute_postgresql_query
from flask_bcrypt import Bcrypt
import os
from groq import Groq

app = Flask(__name__)
bcrypt = Bcrypt(app)
my_secret = os.environ['SECRET_KEY']
app.secret_key = my_secret

def chat_with_groq(client, prompt, model, response_format):
    completion = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        response_format=response_format)

    return completion.choices[0].message.content

def get_summarization(client, user_question, df, model):
    """
    This function generates a summarization prompt based on the user's question and the resulting data. 
    It then sends this summarization prompt to the Groq API and retrieves the AI's response.

    Parameters:
    client (Groqcloud): The Groq API client.
    user_question (str): The user's question.
    df (DataFrame): The DataFrame resulting from the SQL query.
    model (str): The AI model to use for the response.

    Returns:
    str: The content of the AI's response to the summarization prompt.
    """
    prompt = '''
      A user asked the following question pertaining to local database tables:

      {user_question}

      To answer the question, a dataframe was returned:

      Dataframe:
      {df}

    In a few sentences, summarize the data in the table as it pertains to the original user question. Avoid qualifiers like "based on the data" and do not comment on the structure or metadata of the table itself
  '''.format(user_question=user_question, df=df)

    # Response format is set to 'None'
    return chat_with_groq(client, prompt, model, None)


model = "llama3-70b-8192"

# Get the Groq API key and create a Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)

print("Welcome to the InstaSearch Chatbot!")


# Load the base prompt
with open('prompt/base_prompt.txt', 'r') as file:
    base_prompt = file.read()

while True:
    # Get the user's question
    user_question = input("Ask a question: ")

    if user_question:
        # Generate the full prompt for the AI
        full_prompt = base_prompt.format(user_question=user_question)

        # Get the AI's response. Call with '{"type": "json_object"}' to use JSON mode
        llm_response = chat_with_groq(client, full_prompt, model,
                                      {"type": "json_object"})
        print("llm_response:", llm_response)

        result_json = json.loads(llm_response)
        if 'sql' in result_json:
            sql_query = result_json['sql']
            results_df = execute_postgresql_query(sql_query)

            formatted_sql_query = sqlparse.format(sql_query,
                                                  reindent=True,
                                                  keyword_case='upper')

            print("```sql format \n" + formatted_sql_query + "\n```")
            print(results_df.to_markdown(index=False))

            summarization = get_summarization(client, user_question,
                                              results_df, model)
            print(summarization)
        elif 'error' in result_json:
            print("ERROR:", 'Could not generate valid SQL for this question')
            print(result_json['error'])

@app.route("/chat")
def index():
    return render_template('chatbot2.html')

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

@app.route("/chatbot")
def chatbot():
    if 'loggedin' not in session:
        return redirect(url_for('register'))
    return '', 204 
    # if 'loggedin' in session:
    #     cleaned_categories = get_cleaned_categories()
    #     return render_template('Favorite.html',categories=cleaned_categories)
    # return  redirect(url_for('register'))

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
                return redirect(url_for('register'))

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

# @app.route("/product_info")
# def product_info():
#     cleaned_categories = get_cleaned_categories()
#     return render_template('SHOW_product.html',categories=cleaned_categories)


@app.route("/search_result")
def search_results():
    data =request.args
    # data =request.form
    cleaned_categories = get_cleaned_categories()
    posts=load_search_results(data['user_input_to_search_bar'])
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
    post=show_product_func(post_id)
    return render_template('SHOW_product.html',
        categories=cleaned_categories,post=post)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
