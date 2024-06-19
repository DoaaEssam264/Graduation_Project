import pandas as pd
from torch import Tensor, nn
from sentence_transformers import SentenceTransformer

def get_similar_posts(query_results,user_input_to_search_bar):
  model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
  df = pd.DataFrame(query_results.fetchall(), columns=query_results.keys())
  # #\ Generate query embedding and make it in lowercase
  user_input_to_search_bar=user_input_to_search_bar.lower()
  query_embedding = model.encode([user_input_to_search_bar])
  #  Building the FAISS index
  post_embeddings =np.array(df["cap_embedding"].values.tolist())

  dimension = post_embeddings.shape[1]
  index = faiss.IndexFlatL2(dimension)  
  index.add(post_embeddings)
  # Perform the search and adding the distances of nn (all) to df
  distances, indices = index.search(query_embedding, len(df))
  flattened_distances = distances.flatten()
  flattened_indices = indices.flatten()
  df['distance'] = np.nan
  df.loc[flattened_indices, 'distance'] = flattened_distances
  # decrease the distance for captions that have the same as user input respectfully
  query_words = query.split()
  for index, row in df.iterrows():
      found_words = 0
      for word in query_words:
          if word in row["caption"]:
              found_words += 1
      if found_words == len(query_words):
          df.at[index, "distance"] -= df["distance"].min()
      elif found_words > 0:
           df.at[index, "distance"] -=  10
  
  df=df[df['distance']<30]
  df = df.sort_values(by='distance', ascending=True)
  return df.to_dict(orient='records')



  
  

  
  

