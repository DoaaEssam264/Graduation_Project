from sqlalchemy import create_engine, text
import os
from functions import get_similar_posts,clean_category

db_connecton_uri = os.environ['db_connection_uri']
engine = create_engine(db_connecton_uri)

#TO CHECK DB
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT category FROM pages"))
#     usernamess = [row for row in result.all()]
# print(usernamess)



#LOAD RECOMENDED PAGES TO HOME PAGE
def load_homepage_random_recommendations():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM pages ORDER BY RANDOM() LIMIT 4"))
        pages = []
        for page in result.all():
            pages.append(page._mapping)
        return pages 


#LOAD PAGES TO USER SEARCH QUERY
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
        return prod

def get_cleaned_categories():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT category FROM pages"))
        categories = result.fetchall()
    cleaned_categories = []
    for row in categories:
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
    # Convert the rows into a list of dictionaries
    pages = [row._mapping for row in rows]
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
