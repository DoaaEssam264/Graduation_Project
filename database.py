from sqlalchemy import create_engine, text
import os


db_connecton_uri = os.environ['db_connection_uri']
engine = create_engine(db_connecton_uri)
def load_homepage_random_recommendations():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM pages ORDER BY RANDOM() LIMIT 4"))
        pages = []
        for page in result.all():
            pages.append(page._mapping)
        return pages    

# def get_unique_categories():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT category FROM pages"))
#         unique_categories = set()
#         for row in result:
#             categories = row['category'].split(',')
#             print(categories)
#             unique_categories.update(category.strip() for category 
#                   in categories)
#         return sorted(unique_categories)

