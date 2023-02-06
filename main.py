#Import Packages

import pandas as pd
import json
from musixmatch import Musixmatch
musixmatch = Musixmatch('915a5145eef8a1ac16c4a7a69aa8f81c')

import os
import nltk
from nltk.tokenize import RegexpTokenizer
from collections import Counter
import py3langid as langid

#Let's start with the albumid. You can find this on musixmatch by looking at the source code on Chrome.

albumid = 27336583

#Let's import the album metadata to find the artist name and release date. We'll refer to this later.

album_data = musixmatch.album_get(albumid)
album_meta = album_data["message"]["body"]["album"]

#Print album metadata for audit in case there is problems with the code.
# print(album_meta)

#Let's pull out the artist_name and release_date for our dataframe later.

artist_name = (album_meta["artist_name"])
print(artist_name)
release_date = (album_meta["album_release_date"])
print(release_date)

#Now let's import a tracklist of album_id's from the album.
get_album_tracks = musixmatch.album_tracks_get(albumid, 0, 100, '')
get_album = get_album_tracks["message"]["body"]["track_list"]

#This should help us pull out the song title of the first song of the album.
get_first_song_title = get_album[0]["track"]["track_name"]

#Let's keep the track title saved for later to add to our dataframe.
track_title = get_first_song_title
print(track_title)
print('\n')

#This helps us extract the song
track_id = get_album[0]["track"]["track_id"]
  
# print(track_id)
#This should be a list of track_id's from the imported album.abs

#Now, let's find the lyrics. We will use the index[0] since most K-pop albums put their lead single in first position.

import_lyrics = musixmatch.track_lyrics_get(track_id)

#Then let's extract and trim the lyrics.

lyrics = import_lyrics["message"]["body"]["lyrics"]["lyrics_body"]
lyrics_trim = lyrics[:-74]
print(lyrics_trim)


#Now let's write the lyrics into a .txt file in a folder called '/lyrics_txt'

with open(f'lyrics_txt/{artist_name}-{track_title}.txt', 'w') as f:
    f.write(lyrics_trim)
    f.write('\n')

path = f'lyrics_txt/{artist_name}-{track_title}.txt'
# print(release_date)



punc_tokenizer = nltk.RegexpTokenizer(r"\w+")

def k_pop_counter(path):

  with open(path) as f:
    rawline = [word.lower() for line in f for word in line.split()]

  a = []
  for word in rawline:   
    a.append(word.replace('(','').replace(')','') ) 

  b = []
  for word in a:
    b.append(word.replace(',','')) 

  a = []
  for word in b:
    a.append(word.replace('’',''))

  b = []
  for word in a:
    b.append(word.replace('"','')) 

  c = [punc_tokenizer.tokenize(line) for line in b]

  a = []
  for word in c:
    for line in word:
      a.append(line)

  set1 = set(a)

  langid.set_languages(['en', 'ko'])

  langs_tok = []
  for word in a:
    langs_tok.append(langid.classify(word)[0])

  langs_tok_edit = []
  for word in langs_tok:
    if word == 'ko':
      langs_tok_edit.append(word.replace('ko', 'ko_tok'))
    if word == 'en':
      langs_tok_edit.append(word.replace('en', 'en_tok'))
  
  langs_type = []
  for word in set1:
     langs_type.append(langid.classify(word)[0])
    
  langs_type_edit = []
  for word in langs_type:
    if word == 'ko':
      langs_type_edit.append(word.replace('ko', 'ko_type'))
    if word == 'en':
      langs_type_edit.append(word.replace('en', 'en_type'))
  
  type_count = Counter(langs_type_edit)
  tok_count = Counter(langs_tok_edit)
    
  dict1 = dict(type_count)
  dict2 = dict(tok_count)

  dict1.update(dict2)
  return(dict1)

output = (k_pop_counter(path))
print(output)

en_tok = output["en_tok"]
en_type = output["en_type"]
ko_tok = output["ko_tok"]
ko_type = output["ko_type"]


d = {'track_title':[track_title],'release_date':[release_date], 'artist_name':[artist_name], 'ko_tok':ko_tok, 'en_tok': en_tok, 'ko_type':ko_type, 'en_type': en_type}
df = pd.DataFrame(data = d)

df.to_csv(f'dfs/{artist_name}_{track_title}typetok.csv')

# Give the directory you wish to iterate through
my_dir = "/home/runner/MusixMatchPlayTime/dfs"

# Using os.listdir to create a list of all of the files in dir
dir_list = os.listdir(my_dir)

df_list = [pd.read_csv(f'dfs/{f}') for f in dir_list]

df_main = pd.concat(df_list, ignore_index = True)
df_main.to_csv('k_pop_tok_type.csv', sep=',')