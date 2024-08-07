import pandas as pd
from torch import Tensor, nn
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os
import requests

# def get_similar_posts(query_results,user_input_to_search_bar):
#   model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
#   df = pd.DataFrame(query_results.fetchall(), columns=query_results.keys())

#   # #\ Generate query embedding and make it in lowercase
#   user_input_to_search_bar=user_input_to_search_bar.lower()
#   query_embedding = model.encode([user_input_to_search_bar])
#   post_embeddings =np.array(df["cap_embedding"].values.tolist())
#   # Calculate cosine similarity
#   similarities = cosine_similarity(query_embedding, post_embeddings).flatten()
#   df['similarity'] = similarities
#   # increase the sim for captions that have the same as user input respectfully

#   query_words = user_input_to_search_bar.split()
#   for index, row in df.iterrows():
#         found_words = 0
#         for word in query_words:
#             if word in row["caption"]:
#                 found_words += 1
#         if found_words == len(query_words):
#             df.at[index, "similarity"] += 0.3
#         elif found_words > len(query_words)/2:
#             df.at[index, "similarity"] += 0.1

#   df = df[df['similarity'] > 0.7]
#   df = df.sort_values(by='similarity', ascending=False)
#   return df.to_dict(orient='records')

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_similar_posts(query_results,user_input_to_search_bar):
  df = pd.DataFrame(query_results.fetchall(), columns=query_results.keys())
  # #\ Generate query embedding and make it in lowercase
  user_input_to_search_bar=user_input_to_search_bar.lower()
  query_embedding = model.encode([user_input_to_search_bar])
  post_embeddings =np.array(df["cap_embedding"].values.tolist())
  # Calculate cosine similarity
  similarities = cosine_similarity(query_embedding, post_embeddings).flatten()
  df['similarity'] = similarities
  # increase the sim for captions that have the same as user input respectfully

  query_words = user_input_to_search_bar.split()
  for index, row in df.iterrows():
        found_words = 0
        for word in query_words:
            if word in row["caption"]:
                found_words += 1
        if found_words == len(query_words):
            df.at[index, "similarity"] += 0.3
        elif found_words > len(query_words)/2:
            df.at[index, "similarity"] += 0.1

  df = df[df['similarity'] > 0.75]
  df = df.sort_values(by='similarity', ascending=False)
  df = df.head(30)
  os.makedirs('static/images', exist_ok=True)
  for _, ro in df.iterrows():
    if 't51.29350-15' in ro["image"]:
    # Ensure the 'images' directory exists
    # Download images for the filtered posts
        output_path = os.path.join("static/images", f"{ro['post_id']}.png")
        if not os.path.exists(output_path):
            response = requests.get(ro["image"], stream=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
  return df.to_dict(orient='records')

def clean_category(category):
  if category.startswith('new category: '):
      return category.replace('new category: ', '')
  return category


