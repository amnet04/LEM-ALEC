
# coding: utf-8

# # Data treatment

# In[1]:

import numpy as np
import pandas
import re


# ## 1. Constants definition

# ### 1.1. Files and folders

# In[5]:

# Folders
ORIGINAL_DATA_FOLDER="/src/data/originales/"
PROCECED_DATA_FOLDER="/src/data/procesados/"

# original data files
ORIGINAL_FREQ_SOURCE = "{}TWITTER_COLOMBIA_HEADER.csv".format(ORIGINAL_DATA_FOLDER)
ORIGINAL_CITIES_SOURCE = "{}cities_coordinates.csv".format(ORIGINAL_DATA_FOLDER)

# Proceced data files
CLEAN_FREQ_FILE = "{}clean/TWITTER_COLOMBIA_FREQ_CLEAN.csv".format(PROCECED_DATA_FOLDER)
REL_FREQ_DATA_DES = "{}clean/TWITTER_COLOMBIA_RELATIVE_FREQ_CLEAN.csv".format(PROCECED_DATA_FOLDER)
RANK_DATA_DES = "{}clean/TWITTER_COLOMBIA_RANK.csv".format(PROCECED_DATA_FOLDER)
NOR_RANK_DES = "{}clean/TWITTER_COLOMBIA_RANK_NORM.csv".format(PROCECED_DATA_FOLDER)
FILTER_CITIES = "{}/geo/filter_cities_coordinates.csv".format(PROCECED_DATA_FOLDER)


# ## 2. File functions

# In[122]:

def regular_dataframe_to_csv_write(dataframe, destino):
    dataframe.to_csv(
        destino, 
        sep="\t",
        decimal=",",
        encoding='utf-8',
        header=dataframe.columns
    )


# ## 3. Data filtering

# ### 3.1 Word filtering

# In[8]:

def ValidWordsFrame(file):
    general_words_data = pandas.read_csv(
        file, 
        encoding='utf-8', 
        usecols=[*range(0,6)],
        skiprows=[*range(1,6)],
        dtype={'total':np.int32,'lower':np.int32, 'titled':np.int32, 'upper':np.int32, 'other':np.int32},
        index_col = ['#CITY#']
    )
    
    totales = {}
    total= len(general_words_data.index)
    
    #filtrar las palabras con una sola aparición, porque dan hsic malos
    valid_words=general_words_data.loc[general_words_data['total']>1]
    one_app = total - len(valid_words)
    
    #filtrar acronimos
    valid_words=valid_words.loc[valid_words['lower']>valid_words['upper']]
    acronims = total+ one_app - len(valid_words)
    
    #filtrar posibles nombres propios
    valid_words=valid_words.loc[valid_words['lower']>valid_words['titled']]
    personal_names = total+one_app+acronims-len(valid_words)
    
    #obtener palabras válidas hasta aquí
    valid_words = pandas.DataFrame(valid_words.index)
    
    
    # Filtrar otras cosas
    
    # Filtro de posibles links
    http_pat = re.compile(r'.*http.*',flags=re.IGNORECASE)
    valid_words['http'] = valid_words['#CITY#'].str.contains(http_pat)
    valid_words=valid_words.loc[valid_words['http']==False]
    links = total+one_app+acronims+personal_names-len(valid_words)

    # Filtro risas 
    risa_pat = re.compile(r'.*(ja|je|ji|jo|ha|he|hi|ho){2,}.*',flags=re.IGNORECASE)
    valid_words['risa'] = valid_words['#CITY#'].str.extract(risa_pat, expand=True)
    valid_words['risa'] = ~valid_words['risa'].isnull()
    valid_words=valid_words.loc[valid_words['risa']==False]
    laugths = total+one_app+acronims+personal_names+ links-len(valid_words)
    
    # Filtro pics al final, porque no se que es pero me late que es algo de twiter, una foto posiblemente
    pic_pat = re.compile(r'.*pic$',flags=re.IGNORECASE)
    valid_words['pic'] = valid_words['#CITY#'].str.contains(pic_pat)
    valid_words=valid_words.loc[valid_words['pic']==False]
    pics = total+one_app+acronims+personal_names+ links+ laugths -len(valid_words)
    
    # Filtro palabras con mucha repetición de letras (más de tres letras iguales repetidas)
    multiple_path = re.compile(r'(\w)\1{2,}',flags=re.IGNORECASE)
    valid_words['multiple'] = valid_words['#CITY#'].str.extract(multiple_path, expand=True)
    valid_words['multiple'] = ~valid_words['multiple'].isnull()    
    valid_words=valid_words.loc[valid_words['multiple']==False]
    multiple = total+one_app+acronims+personal_names+ links+ laugths + pics -len(valid_words)
    
    # Filtro palabras con numeros
    numeros_path = re.compile(r'.*(\d).*',flags=re.IGNORECASE)
    valid_words['numeros'] = valid_words['#CITY#'].str.extract(multiple_path, expand=True)
    valid_words['numeros'] = ~valid_words['numeros'].isnull()
    valid_words=valid_words.loc[valid_words['numeros']==False]
    valid_words=valid_words.set_index('#CITY#')
    with_numbers = total+one_app+acronims+personal_names+ links+ laugths + pics + multiple -len(valid_words)
    
    filter_sum = one_app+acronims+personal_names+ links+ laugths + pics + multiple + with_numbers
    filter_len = len(valid_words)
    
    return(valid_words.index)


# In[9]:

ValidWords=ValidWordsFrame(ORIGINAL_FREQ_SOURCE)


# ## 3.2 Cities filtering

# In[6]:

def vocabulary_data(file):
    general_cities_data =pandas.read_csv(
        file, 
        encoding='utf-8',
        nrows=5,
        index_col = ['#CITY#']
    )
    general_cities_data.drop(labels=['total','lower', 'titled', 'upper','other'], axis=1, inplace=True)
    general_cities_data.drop(labels=['#COUNTRY#','#TWEETS#', '#USERS#'], axis=0, inplace=True)
    general_cities_data=general_cities_data.transpose()
    max_words = general_cities_data['#TOTAL_WORDS#'].max()
    max_vocabulary_size = general_cities_data['#VOCABULARY_SIZE#'].max()
    return(max_words, max_vocabulary_size, general_cities_data)


# In[7]:

max_w, max_v, Vocabulary_Data = vocabulary_data(ORIGINAL_FREQ_SOURCE)


# In[127]:

def FilterCitiesBy(data, order_by=False, word_tresh=0, vocabulary_tresh=0):
    localidades_filtradas = data
    localidades_filtradas['#TOTAL_WORDS#']=localidades_filtradas['#TOTAL_WORDS#'].apply(pandas.to_numeric)
    localidades_filtradas['#VOCABULARY_SIZE#']=localidades_filtradas['#VOCABULARY_SIZE#'].apply(pandas.to_numeric)
    if word_tresh != 0:
        localidades_filtradas = localidades_filtradas.loc[localidades_filtradas["#TOTAL_WORDS#"]>=word_tresh]
    if vocabulary_tresh != 0:
        localidades_filtradas = localidades_filtradas.loc[localidades_filtradas["#VOCABULARY_SIZE#"]>=vocabulary_tresh]
    if order_by:
        localidades_filtradas = localidades_filtradas.sort_values(by=order_by)
    else:
        localidades_filtradas = localidades_filtradas
    return(localidades_filtradas.index)


# In[128]:

ValidCities = FilterCitiesBy(Vocabulary_Data, order_by=False, word_tresh=50000, vocabulary_tresh=0)


# In[155]:

def valid_cities_coordinates(origin, destination, ValidCities):
    all_cities_coordinates =pandas.read_csv(
        origin, 
        encoding='utf-8',
        sep="\t",
        decimal=",",
        index_col = ['ciudad']
    )
    cities_to_drop = list(set(list(all_cities_coordinates.index))-set(ValidCities))
    valid_cities = all_cities_coordinates.drop(labels=cities_to_drop)
    regular_dataframe_to_csv_write(valid_cities, destination)
    


# ### 3.3. Apply words an cities filters to all data

# In[131]:

def FiltredWordLocationFrame(origin, destination, ValidCities, ValidWords ):
    lenvalidcities=len(ValidCities)
    
    file_word_freq = pandas.read_csv(
        origin, 
        encoding='utf-8',
        chunksize=10000, 
        index_col=0,
        skiprows=[1,3,5],
        sep =",", 
        quotechar='"'
    )
    
    i=0
    for chunk in file_word_freq:
        cities_to_drop = list(set(list(chunk.columns))-set(ValidCities))
        words_to_drop = list(set(list(chunk.index))-set(ValidWords))
        chunk.drop(labels=cities_to_drop, axis=1, inplace=True)
        chunk.drop(labels=words_to_drop, inplace=True)
        if i==0:
            filtredwordsfreq=chunk
        else:
            filtredwordsfreq=filtredwordsfreq.append(chunk)
        print('\rLoop {}. Borrados = {}, tamaño actual del arreglo: {}'.format(i, len(words_to_drop), len(filtredwordsfreq)), end="\t\t\t")
        i+=1
    totales=pandas.DataFrame(filtredwordsfreq.sum(),columns=['#TOTAL_WORDS#']).transpose()
    filtredwordsfreq = pandas.concat([totales, filtredwordsfreq])    
            
    regular_dataframe_to_csv_write(filtredwordsfreq, destination)
        
    print('\r Listo!!', end="\t\t\t\t\t\t")   


# In[ ]:

def relative_freq_file(file,destino):
    file_word_freq = pandas.read_csv(
        file, 
        encoding='utf-8', 
        index_col=0,
        sep ="\t",
        decimal=",",
        quotechar='"'
    )
    frecuencias_relativas = file_word_freq.iloc[0:]/file_word_freq.iloc[0]
    frecuencias_relativas.to_csv(destino, sep="\t",decimal=",",header=frecuencias_relativas.columns)


# In[ ]:

def rank_file(file,destino):
    file_word_rank = pandas.read_csv(
        file, 
        encoding='utf-8', 
        index_col=0,
        skiprows=[1],
        sep ="\t",
        decimal=",",
        quotechar='"'
    )
    file_word_rank = file_word_rank.rank(method='dense',ascending=False)
    max_rank = file_word_rank.max(axis=0)
    file_word_rank = pandas.concat([pandas.DataFrame(max_rank, columns=['#MAX_RANK#']).transpose(), file_word_rank])    
    file_word_rank = file_word_rank.astype(int)
    file_word_rank.to_csv(destino, sep="\t",decimal=",",header=file_word_rank.columns)


# In[ ]:

def normaliced_rank_file(file,destino):
    normaliced_word_rank = pandas.read_csv(
        file, 
        encoding='utf-8', 
        index_col=0,
        sep ="\t",
        decimal=",",
        quotechar='"'
    )
    normaliced_word_rank = (normaliced_word_rank.iloc[0:]/normaliced_word_rank.iloc[0])*100000000
    normaliced_word_rank.to_csv(destino, sep="\t",decimal=",",header=normaliced_word_rank.columns)


# In[22]:

general_words_data = pandas.read_csv(
        "/src/data/procesados/clean/TWITTER_COLOMBIA_FREQ_CLEAN.csv", 
        encoding='utf-8',
        sep ="\t",
        decimal=",",
        #usecols=[*range(0,6)],
        #skiprows=[*range(1,:)],
        dtype={'total':np.int32,'lower':np.int32, 'titled':np.int32, 'upper':np.int32, 'other':np.int32},
        index_col = [0]
    )


# In[28]:

general_words_data.loc["#TOTAL_WORDS#"].mean()


# In[ ]:



