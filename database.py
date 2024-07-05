from sqlalchemy import create_engine, text
import os
import numpy as np
import pandas as pd
from functions import get_similar_posts,clean_category
import google.generativeai as genai
import io
import PIL.Image as Image
from io import BytesIO
import base64

db_connecton_uri = os.environ['db3']
engine = create_engine(db_connecton_uri)
api_key = os.environ['api_key']
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
model2 =genai.GenerativeModel("gemini-1.5-flash")
base_model = genai.GenerativeModel('gemini-1.5-flash')
chat = base_model.start_chat(history=[])
print(chat.history)

def clean_sql_query(query):
    if query.startswith("[SQL:"):
        query = query[5:]  # Remove '[SQL: ' from the start
    if query.endswith("]"):
        query = query[:-1]  # Remove ']' from the end
    return query

def generate_gemini_response(user_input):
    
    prompt1 = """ You are an expert in converting English user questions to PostgreSQL code:

        The first PostgreSQL table, named `posts`, has the following columns:
        - caption (TEXT): The caption of the post contains the product being selled in the post like lipgloss,jeans, hair serum, sunblock,eyliner,laptops,tshirts,tops and more.
        - commentscount (INT4): The number of comments on the post
        - likescount (INT8): The number of likes on the post
        - commentscount (INT4): The number of comments on the post.
        - likescount (INT8): The number of likes on the post.
        - timestamp (VARCHAR): The timestamp when the post was created.
        - pagename (VARCHAR): The username of the page.
        - category (VARCHAR): The category the post belongs to.
        - score (FLOAT8): The score indicating how accurately the post belongs to this category.
        - rating (FLOAT8): The rating of the product.
        - bio (VARCHAR): The bio of the page, sometimes containing information like location or slogan or branches of stores .
        - posturl (VARCHAR): The URL of the post.
        - product (VARCHAR): contains the product being selled in the post.
        - pageurl (VARCHAR): The URL of the page's profile.

        The second PostgreSQL table, named `pages`, has the following columns:
        - verified (BOOL): Indicates if the page is verified.
        - biography (VARCHAR): The biography of the page, sometimes containing information like location or slogan or branches of stores .
        - isbusinessaccount (BOOL): Indicates if the account is a business account.
        - followerscount (INT8): The number of followers the page has.
        - postscount (INT4): The number of posts the page has created.
        - joinedrecently (BOOL): Indicates if the page has joined recently.
        - page_username (VARCHAR): The username of the page.
        - rate (FLOAT8): The rate associated with the page.
        - category (VARCHAR): A list of categories the page has, which are {categories}, these only are the categories in the database dont query on others but them.
        - url (VARCHAR): The URL of the page's profile.

        Examples:
        1. which pages sell mom-fit jeans?
        SELECT pages.page_username, pages.url FROM pages INNER JOIN posts ON pages.page_username = posts.pagename WHERE (posts.product LIKE '%mom-fit jeans%'
         OR posts.caption LIKE '%mom-fit jeans%'
         OR posts.caption LIKE '%mom fit jeans%'
         OR posts.caption LIKE '%mom-fit jean%'
         OR posts.caption LIKE '%mom fit jean%'
         OR posts.caption LIKE '%momfit jeans%'
         OR posts.caption LIKE '%momfit jean%'
         OR posts.category LIKE '%mom-fit jeans%')
         OR posts.product LIKE '%mom fit jeans%,
         OR posts.product LIKE '%mom-fit jean%'
         OR posts.product LIKE '%mom fit jean%'
         OR posts.product LIKE '%momfit jeans%'
         OR posts.product LIKE '%momfit jean%';


        2.Recommend pages that sell clothes?
        SELECT pages.page_username, pages.url FROM pages INNER JOIN posts ON pages.page_username = posts.pagename WHERE 
        (posts.category LIKE '%clothing%' OR posts.product LIKE '%clothing%' OR posts.caption LIKE '%clothing%');


        3.  what is the best page that sells sets?
        SELECT pages.page_username, pages.url FROM pages INNER JOIN posts ON pages.page_username = posts.pagename WHERE (posts.product LIKE '%sets%' OR posts.product LIKE '%set%' OR posts.caption like %sets% OR posts.caption like %set%) ORDER BY pages.rating DESC LIMIT 1;



        4.tell me pages that sell rings?
        SELECT pages.page_username, pages.url FROM  pages INNER JOIN posts ON pages.page_username = posts.pagename WHERE (posts.product LIKE '%rings%' OR posts.product LIKE '%ring%' OR posts.caption LIKE '%rings%' OR posts.caption LIKE '%ring%');



        5.page that has bags
        SELECT pages.page_username, pages.url FROM pages INNER JOIN posts ON pages.page_username = posts.pagename WHERE (posts.product LIKE '%bags%' OR posts.product LIKE '%bag%' OR posts.category LIKE '%bags%' OR posts.category LIKE '% bag%' OR posts.caption LIKE '%bags%');



        6.pages that has cross-bags
        SELECT pages.page_username, pages.url FROM pages INNER JOIN posts ON pages.page_username = posts.pagename WHERE (posts.product LIKE '%cross-bags%' OR posts.caption LIKE '% cross-bags%' OR posts.product LIKE '%cross bag%' OR posts.product LIKE '%cross bags%' OR posts.product LIKE '%cross-bag%' OR posts.caption LIKE '%cross bag%' OR posts.caption LIKE '%cross bags%' OR posts.caption LIKE '%cross-bag%';



        7.pages that has beach mats
        SELECT pages.page_username, pages.url FROM pages INNER JOIN posts ON pages.page_username = posts.pagename WHERE (posts.caption LIKE '%beach mats%' OR posts.caption LIKE '%beach mats%' OR posts.caption LIKE '%beachy mats%' OR posts.caption LIKE '%beaches mats%' OR posts.caption LIKE '%beachy mat%' OR posts.product LIKE '%beach mats%' OR posts.product LIKE '%beach mats%' OR posts.product LIKE '%beachy mats%' OR posts.product LIKE '%beaches mats%' OR posts.product LIKE '%beachy mat%';





        Rules for querying the dataset:
        * if the question is searching for a product name query with like from column caption
        * if you queried using category from posts only order by score desc
        * if you queried using category from pages use like
        * select all usually
        *if the what u are searching for is not in this category list {categories}, search in caption from table posts instead
        * make INNER JOIN pages ON posts.pagename = pages.page_username if you are using category from pages and caption from posts in one query

        Question:
        --------
        {user_question}
        --------

        Reminder: Generate a PostgreSQL SQL query to answer the question:
        * Ensure that the query is flexible enough to handle synonyms or similar terms (e.g., searching for "beach mats" should also retrieve results for "beachy mat").
        * If the question cannot be answered with the available tables, return 'No data' and the user question itself.
        * Ensure that the entire output is returned on a single line as text, the SQL query only without any other details like SQL tags or \n.
        * Keep your query as simple and straightforward as possible; do not use subqueries.
        * Don't start your answer with [SQL: SELECT ...  ],
        Answer with : Select ...



        """
    prompt2 = """ You are a Question Answering bot in a website that answers user questions about pages and the products they include.

              A user asked the following question and this is the dataframe that you should answer from:

              {user_question}

              To answer the question, a dataframe was returned:

              Dataframe:
                {df}

            In a few sentences, summarize the data in the table as to answers to the original user question and return the usernames or pagenames and pageurls or url. Avoid qualifiers like "based on the data" and do not comment on the structure or metadata of the table itself
            and be friendly with the user and if df returned is no data return "be more specific", dont give information about tables or df just be general. if user asked about pages make sure to return the pagename and its url.
          """
    base_prompt = """ You are an expert at converting user questions into grammatically different versions of the user question putting into consideration chat history .
    Your role is to rephrase the user question, Perform query decomposition. Given a user question without any creativity try to widen it in terms of spelling and grammar ,make it plural or singular for example and do not makeup questions by yourself.
    The user question is: {user_question} it is not including any greetings or salutations.
    Return the most expressive questions only according to the question.
    For example: user question: " Tell me pages that sell pants ." , you will generate "Tell me pages that sells pant" and "Tell me pages that sell pants"
    Another example: user question: " Suggest pages that have mom-fit jeans", you will generate " Suggest pages that have mom-fit jean" and " Suggest pages that have mom fit jeans
    Anther example : user question " tell me a page that sells beach mats" , you will generate "Tell me a page that sells beach mat" and "Tell me a page that sells beachy mats" and "Tell me a page that sells beachy mat"
    Another example : user question " what is the best page?" or "which are the top rated" or "what is the best one" or anything looks like this, you will look at the history an know what is the user talking about then you will generate "What is the best page for beach mat" and "What is the best page for beach mats"
    Another example:user question: " hi" or " hello", you will not generate any question or rephrase anything just reply with" Hi!"
    Always return the main user question that the user will ask accompanied with its other grammartically different question separated by 'OR'
    the chat history to make the questions more clear if needed: {chat_history}
    Try to make the words plural and in many other forms in order to make my sql queries more flexible
    If there are acronyms or words you are not familiar with, do not try to rephrase them."""



    categories = get_cleaned_categories()
    query= chat.send_message(base_prompt.format(user_question=user_input, chat_history=chat.history))
    print(query.text)
    query = model.generate_content(
        prompt1.format(user_question=query.text, categories=categories))
    print(query.text)
    query=clean_sql_query(query.text)
    # query=query.text
    ans = ""
    df = query
    if not df.startswith("No data"):
        with engine.connect() as conn:
            result = conn.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            print(df)
    ans = model2.generate_content(prompt2.format(user_question=user_input, df=df)).text
    print(ans)
    return ans

def load_homepage_random_recommendations():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM pages ORDER BY RANDOM() LIMIT 4"))
        rand = result.fetchall()
        columns = result.keys()
        pages = [dict(zip(columns, row)) for row in rand]
        for page in pages:
            image_data = page.get('image')
            if image_data:
                # base64_image = base64.b64encode(image_data).decode('utf-8')
                page['image'] = f"data:image/jpeg;base64,{image_data}"

    return pages

def load_search_results(user_input_to_search_bar):
    with engine.connect() as conn:  
        result=conn.execute(text("SELECT * FROM posts")) 
    return get_similar_posts(result,user_input_to_search_bar)

def show_product_func(post_id):
    query = text("""
        SELECT * 
        FROM posts 
        WHERE post_id = :post_id """)
    with engine.connect() as conn:
        result = conn.execute(query, {"post_id": post_id})
        product = result.fetchone()
        cols=result.keys()
        prod = dict(zip(cols, product))
        str_id=str(prod['post_id'])
        return prod , str_id

def get_cleaned_categories():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT category FROM pages"))
        categories = result.fetchall()
    cleaned_categories = []
    for row in categories:
      if row[0] !="no_cat":
        category_list = eval(row[0])  # Assuming the categories are stored as a string representation of a list
        for category in category_list:
            cleaned_categories.append(clean_category(category).title())

    unique_cleaned_categories = list(set(cleaned_categories))
    return sorted(unique_cleaned_categories)

def get_favorite_posts(log_username):
    query = text("""
        SELECT p.* 
        FROM fav f 
        JOIN posts p ON f.fav_post_id = p.post_id 
        WHERE f.log_username = :log_username
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"log_username": log_username})
        favorite_posts = result.fetchall()
        columns=result.keys()
        favorite_posts_dicts = [dict(zip(columns, row)) for row in favorite_posts]
    return favorite_posts

def get_pages_of_a_certain_category(category):
    # geting all pages that belong to a specific category
    specific_category = f"%'{category}'%"
    with engine.connect() as conn:
          result = conn.execute(text("""SELECT * FROM pages 
          WHERE category LIKE :specific_category"""),     
          {'specific_category': specific_category})
          rows = result.fetchall()
          columns = result.keys()
          pages = [dict(zip(columns, row)) for row in rows]
          for page in pages:
              image_data = page.get('image')
              if image_data:
                  # base64_image = base64.b64encode(image_data).decode('utf-8')
                  page['image'] = f"data:image/jpeg;base64,{image_data}"
    return pages

def load_user(login_username):
    with engine.connect() as conn:
        info = conn.execute(text("SELECT * FROM user_info WHERE login_username = :login_username"), {"login_username": login_username})
        result = info.fetchone()
        if result:
          return (result[0], result[2])
    return None

def add_user(login_username, email, hashed_password):
    with engine.connect() as conn:
        trans = conn.begin()
        conn.execute(text("INSERT INTO user_info (login_username, email, password) VALUES (:login_username, :email, :password)"),
                          {"login_username": login_username, "email": email, "password": hashed_password})
        trans.commit()

def number_of_fav_posts(username):
    query = text("""
        SELECT COUNT(DISTINCT fav_post_id) AS liked_count
        FROM fav
        WHERE log_username = :username
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"username": username})
        liked_count = result.fetchone()[0]
    return liked_count

def add_post_to_favorites(log_username, fav_post_id):
    print("first",log_username)
    log_username = str(log_username)
    print("second",log_username)
    with engine.connect() as conn:
        trans = conn.begin()
        conn.execute(text("INSERT INTO fav (log_username, fav_post_id) VALUES (:log_username, :fav_post_id)"), {"log_username": log_username, "fav_post_id": fav_post_id})
        trans.commit()

def remove_post(log_username, post_id):
    with engine.connect() as conn:
        trans = conn.begin()
        conn.execute(text("DELETE FROM fav WHERE log_username = :log_username AND fav_post_id = :post_id"), {"log_username": log_username, "post_id": post_id})
        trans.commit()

def upsert_favTable(log_username, post_id, rating, page_username):
    check_query = text("SELECT log_username, post_id FROM post_rating WHERE log_username = :log_username AND post_id = :post_id")

    with engine.connect() as conn:
        result = conn.execute(check_query, {"log_username": log_username, "post_id": post_id})
        exists = result.fetchone() is not None

    if exists:
        update_query = text("UPDATE post_rating SET rating = :rating, page_username = :page_username WHERE log_username = :log_username AND post_id = :post_id")
        with engine.connect() as conn:
            trans = conn.begin()
            conn.execute(update_query, {"log_username": log_username, "post_id": post_id, "rating": rating, "page_username": page_username})
            trans.commit()
    else:
        insert_query = text("INSERT INTO post_rating (log_username, post_id, rating, page_username) VALUES (:log_username, :post_id, :rating, :page_username)")
        with engine.connect() as conn:
            trans = conn.begin()
            conn.execute(insert_query, {"log_username": log_username, "post_id": post_id, "rating": rating, "page_username": page_username})
            trans.commit()
    update_rating_TABLEposts(post_id)

def get_post_avg_rating(post_id):
    query = text("""
        SELECT AVG(rating) AS avg_rating
        FROM post_rating
        WHERE post_id = :post_id
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"post_id": post_id})
        avg_rating = result.fetchone()[0]
        if avg_rating is None:
          return 0
        else:
          return round(avg_rating, 1)

def update_rating_TABLEposts(post_id):
    rating=get_post_avg_rating(post_id)
    query = text(""" UPDATE posts SET rating = :rating WHERE post_id = :post_id """)
    with engine.connect() as conn:
        trans = conn.begin()
        result = conn.execute(query, {"post_id": post_id, "rating": rating})
        trans.commit()

def get_avgpage_rating(page_username):
    check_query = text("SELECT AVG(rating) AS avg_Page_rating FROM post_rating WHERE page_username = :page_username")
    with engine.connect() as conn:
        result = conn.execute(check_query, {"page_username": page_username})
        avg_Page_rating = result.fetchone()[0] 
        return round(avg_Page_rating, 1)

def update_page_avg_rating(page_username):
    query = text(""" UPDATE pages SET rate = :rate WHERE page_username = :page_username """)
    rate=get_avgpage_rating(page_username)
    with engine.connect() as conn:
        trans = conn.begin()
        result = conn.execute(query, {"rate": rate, "page_username": page_username})
        trans.commit()

def insert(username, searched_products):
    # Insert query
    insert_query = text("""
    INSERT INTO recommendations (username, searched_products)
    VALUES (:username, :searched_products);
    """)
    with engine.connect() as conn:
        trans = conn.begin()  
        conn.execute(insert_query, {'username': username, 'searched_products': searched_products})
        trans.commit()
        print("Data inserted successfully.")
