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
    pages = [dict(row) for row in rows]
    return pages