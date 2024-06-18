from sqlalchemy import create_engine, text
import os


db_connecton_uri = os.environ['db_connection_uri']
engine = create_engine(db_connecton_uri)
def load_homepage_random_recommendations():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM pages ORDER BY RANDOM() LIMIT 30"))
        pages = []
        for page in result.all():
            pages.append(page._mapping)
        return pages    