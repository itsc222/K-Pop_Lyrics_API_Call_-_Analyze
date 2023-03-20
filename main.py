#Import Packages

import polars as pl
from musixmatch import Musixmatch

musixmatch = Musixmatch('915a5145eef8a1ac16c4a7a69aa8f81c')

import nltk
from nltk import RegexpTokenizer
import py3langid as langid

#This is an empty data set to create the columns of our main mega_meta_df
mega_meta_data = {
  "track_name": [],
  "artist_name": [],
  "release_date": [],
  "track_id": []
}

#This is an empty data set to creat columns of our all_word_df
all_word_df_data = {"track_id": [],
                    "word": [], 
                    "lang_id": [], 
                    "lang_val": []}

#This is our all_word_df
all_word_df = pl.DataFrame(all_word_df_data,
                  schema={"track_id": pl.Int64,
                          "word": pl.Utf8,
                          "lang_id": pl.Utf8,
                          "lang_val": pl.Float64})

#Now let's make the mega_meta_df
mega_meta_df = pl.DataFrame(mega_meta_data,
                            schema={
                              "track_name": pl.Utf8,
                              "artist_name": pl.Utf8,
                              "release_date": pl.Utf8,
                              "track_id": pl.Int64
                            })

#Let's also keep an empty list for collecting track_ids for collecting lyrics later.
track_id_collection = []
track_id_collection_len = len(track_id_collection)

#Let's start with the chart. You can find this on musixmatch by looking at the source code on Chrome.
chart = musixmatch.chart_tracks_get(1, 100, f_has_lyrics=True, country='jp')

#We need the length of the number of tracks in order to index in a FOR loop.
chart_count = len(chart["message"]["body"]["track_list"])
chart_count_index = chart_count - 1

#index for future FOR loop.
index = list(range(chart_count))
# print(index)

for i in index:

  chart_message = chart["message"]["body"]["track_list"][i]["track"]

  #We need the track ID
  track_id = chart_message["track_id"]
  # print(track_id)
  track_id_collection.append(track_id)

  #We need the track name.
  track_name = chart_message["track_name"]
  # print(track_name)

  #We need the artist name.
  artist_name = chart_message["artist_name"]
  # print(artist_name)

  #API Call for Album Metadata so we can add the release date for the song.
  album_id = chart_message["album_id"]
  album_data = musixmatch.album_get(album_id)
  album_message = album_data["message"]["body"]["album"]

  date = album_message["album_release_date"]
  # print(date)

  metadata = {
    "track_id": [track_id],
    "track_name": [track_name],
    "artist_name": [artist_name],
    "release_date": [date]
  }
  # print(metadata)

  #Build a dataframe for the track metadata.
  metadf = pl.DataFrame(metadata,
                        schema={
                          "track_name": pl.Utf8,
                          "artist_name": pl.Utf8,
                          "release_date": pl.Date,
                          "track_id": pl.Int64
                        })

  mega_meta_df.extend(metadf)

# mega_meta_df.write_csv('meta_df.csv', sep=',')

#This is to tokenize the songs later.
punc_tokenizer = nltk.RegexpTokenizer(r"\w+")

for id in track_id_collection:

  #Now, let's find the lyrics. We will use the index[0] since most K-pop albums put their lead single in first position.

  import_lyrics = musixmatch.track_lyrics_get(id)

  #Then let's extract and trim the lyrics.

  lyrics = import_lyrics["message"]["body"]["lyrics"]["lyrics_body"]
  lyrics_trim = lyrics[:-74]

  # print(lyrics_trim)

  a = lyrics_trim.lower()

  b = ' '.join(a.splitlines())
  # print(q)
  
  c = b.split(' ')
  # print(z)

  
  d = [punc_tokenizer.tokenize(word) for word in c]
  e = []
  for list in d:
    e.append(''.join(list))

  f = [i for i in e if i]
  
    


  # print(lyrics_trim)

  # Now let's write the lyrics into a .txt file in a folder called '/lyrics_txt'



  #Let's import the album metadata to find the artist name and release date. We'll refer to this later.


  langid.set_languages(['en', 'ko', 'es', 'ja'])

  for word in f:

    data2 = pl.DataFrame({
       "track_id": [id],
        "word": [word],
        "lang_id": [langid.classify(word)[0]],
        "lang_val": [langid.classify(word)[1]]
      })
    data = {"track_id": [], 
            "word": [], 
            "lang_id": [], 
            "lang_val": []}

    df = pl.DataFrame(data,
                       schema={
                          "track_id": pl.Int64,
                         "word": pl.Utf8,
                         "lang_id": pl.Utf8,
                         "lang_val": pl.Float64
                       }
                     )
      # print(data2)
    df.extend(data2)
      # print(df)
    all_word_df.extend(df)


# Importing the os module
# import os

# # Give the directory you wish to iterate through
# my_dir = "/home/runner/MusixMatchAPIwithTokenization/lyrics_txt"

# # Using os.listdir to create a list of all of the files in dir
# dir_list = os.listdir(my_dir)
# # print(dir_list)

# # Use the for loop to iterate through the list you just created, and open the files

  

# all_word_df.write_csv('all_word_df.csv', sep=',')

full_data_df = mega_meta_df.join(all_word_df, on = "track_id")

full_data_df.write_csv('musixmatch-top100-lyrics.csv', sep=',')