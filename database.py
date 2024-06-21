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


def load_user(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM user_info WHERE login_username = :username"), {"username": username}).fetchone()
        if result:
            return result['login_username'], result['password']
    return None


def add_user(username, email, hashed_password):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO user_info (login_username, email, password) VALUES (:username, :email, :password)"),
                     {"login_username": username, "email": email, "password": hashed_password})
    