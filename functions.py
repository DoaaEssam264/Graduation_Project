import pandas as pd
from torch import Tensor, nn
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import io
import PIL.Image as Image
from io import BytesIO
import base64


def get_similar_posts(query_results,user_input_to_search_bar):
  model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
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
  
  df = df[df['similarity'] > 0.7]
  df = df.sort_values(by='similarity', ascending=False)
  for _,post in df.iterrows():
        if post['post_image']!="static/no_img":
            # base64_image = base64.b64encode(post['post_image']).decode('utf-8')
            post['post_image'] = post["image"]
  return df.to_dict(orient='records')

def clean_category(category):
  if category.startswith('new category: '):
      return category.replace('new category: ', '')
  return category


  
