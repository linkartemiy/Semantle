import gensim
import random
import pathlib
import os
from dotenv import load_dotenv

load_dotenv()


class Model:
    def __init__(self):
        self.model_path = pathlib.Path(__name__).parent.resolve().joinpath(os.getenv('MODEL_PATH'))
        self.dictionary_path = pathlib.Path(__name__).parent.resolve().joinpath(os.getenv('DICTIONARY_PATH'))
        self.model_binary = False
        if self.model_path.endswith('.bin'):
            self.model_binary = True
        self.loadRussianDictionary()
        self.model = gensim.models.KeyedVectors.load_word2vec_format(
            self.model_path, binary=self.model_binary)

    def loadRussianDictionary(self):
        self.rus_arr = []
        with open(self.dictionary_path, 'r', encoding="utf-8") as f:
            st = f.readline()
            while st:
                self.rus_arr.append(f.readline().replace("\n", ""))
                st = f.readline()

    def getRandomWord(self):
        return random.sample(self.rus_arr, 1)
        #return random.sample(self.model.index_to_key, 1)


# import io, numpy as np

#model_fasttext = {}

# fasttext_file = io.open('ruwikiruscorpora_upos_skipgram_300_2_2018.vec',
#                         'r',
#                         encoding='utf-8',
#                         newline='\n',
#                         errors='ignore')

# # For each line in the file, representing a single word vector, store the word itself as the key of the dictionary and
# # the values of its corresponding word vector as the values of the dictionary.
# for line in fasttext_file:
#     values = line.split()
#     word = values[0]
#     coefs = np.asarray(values[1:], dtype='float32')
#     model_fasttext[word] = coefs
#model = gensim.models.KeyedVectors.load(
#    'ruwikiruscorpora_upos_skipgram_300_2_2018.vec')
#model = gensim.models.KeyedVectors.load_word2vec_format('tayga_1_2.vec',
#                                                        binary=False)

# import multiprocessing
# from gensim import FastText

# fn_c, fn_wv = 'b_x.txt', 'b_ft.model'
# print('Создание fasttext-модели по файлу', fn_c)
# sg, size, window, min_cnt, n_iter = 0, 150, 3, 1, 100
# workers = multiprocessing.cpu_count()
# model = FastText(corpus_file=fn_c,
#                  size=size,
#                  window=window,
#                  min_count=min_cnt,
#                  sg=sg,
#                  workers=workers,
#                  iter=n_iter)