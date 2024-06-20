from sqlalchemy import create_engine, text
import os
# from functions import get_similar_posts

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
            text("SELECT * FROM pages ORDER BY RANDOM() LIMIT 20"))
        pages = []
        for page in result.all():
            pages.append(page._mapping)
        return pages 


#LOAD PAGES TO USER SEARCH QUERY
def load_search_results(user_input_to_search_bar):
    with engine.connect() as conn:  
        result=conn.execute(text("SELECT * FROM posts")) 
    return get_similar_posts(result,user_input_to_search_bar)



def clean_category(category):
    if category.startswith('new category: '):
        return category.replace('new category: ', '')
    return category

def get_cleaned_categories():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT category FROM pages"))
        categories = result.fetchall()
    cleaned_categories = []
    for row in categories:
        category_list = eval(row[0])  # Assuming the categories are stored as a string representation of a list
        for category in category_list:
            cleaned_categories.append(clean_category(category))

    unique_cleaned_categories = list(set(cleaned_categories))
    return unique_cleaned_categories

cleaned_categories = get_cleaned_categories()
print(cleaned_categories)