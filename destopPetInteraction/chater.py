import os
import time
import json
import jieba
import gensim
import argparse

class Chater():
    def __init__(self):
        # 解析参数
        parser = argparse.ArgumentParser(description='问答机器人参数')
        parser.add_argument('--data_filepath', default='destopPetInteraction/data/WebQA.v1.0.json')  # 语料路径
        parser.add_argument('--stopwords_filepath', default='destopPetInteraction/data/stopwords.txt')  # 停用词路径
        parser.add_argument('--splitdata_filepath', default='destopPetInteraction/data/splitdata.json')  # 分词结果路径
        parser.add_argument('--dictionary_filepath', default='destopPetInteraction/data/dictionary')  # gensim字典路径
        parser.add_argument('--model_filepath', default='destopPetInteraction/data/tfidf.model')  # tfidf模型路径
        parser.add_argument('--index_filepath', default='./destopPetInteraction/data/tfidf.index')  # 相似度比较序列路径
        args = parser.parse_args()

        # 语料库
        with open(args.data_filepath, encoding='utf-8') as f:
            self.data = json.load(f)
            print("data_file ok")

        # 停用词
        with open(args.stopwords_filepath, encoding='utf-8') as f:
            self.stoplist = f.read().splitlines()

        beg = time.time()
        print('分词中...')
        splitdata_filepath = args.splitdata_filepath
        if os.path.exists(splitdata_filepath):
            with open(splitdata_filepath, encoding='utf-8') as f:
                content = json.load(f)
        else:
            content = []  # 已分词且去停用词的问题
            for key, value in self.data.items():
                question = value['question']
                content.append(self._split_word(question, self.stoplist))
            with open(splitdata_filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(content, ensure_ascii=False))
        print('分词耗时 {:.2f}s'.format(time.time() - beg))

        beg = time.time()
        # 加载gensim字典，若无则生成
        dictionary_filepath = args.dictionary_filepath
        if os.path.exists(dictionary_filepath):
            self.dictionary = gensim.corpora.Dictionary.load(dictionary_filepath)
        else:
            self.dictionary = gensim.corpora.Dictionary(content)
            self.dictionary.save(dictionary_filepath)
        print('gensim字典耗时 {:.2f}s'.format(time.time() - beg))

        beg = time.time()
        num_features = len(self.dictionary)  # 特征数

        # 加载tfidf模型，若无则生成
        model_filepath = args.model_filepath
        if os.path.exists(model_filepath):
            self.tfidf = gensim.models.TfidfModel.load(model_filepath)
        else:
            corpus = [self.dictionary.doc2bow(line) for line in content]  # 语料转词袋表示
            self.tfidf = gensim.models.TfidfModel(corpus)  # 构建tfidf模型
            self.tfidf.save(args.model_filepath)  # 保存tfidf模型

        # 加载tfidf相似度比较序列，若无则生成
        index_filepath = args.index_filepath
        print("cyw!!!", index_filepath)
        self.index_pth = args.index_filepath
        self.num_feature = num_features
        if os.path.exists(index_filepath):
            self.index = gensim.similarities.Similarity.load(index_filepath)
        else:
            self.index = gensim.similarities.Similarity(args.index_filepath, self.tfidf[corpus],
                                                        num_features)  # 文本相似度序列
            self.cc = corpus
            self.index.save(index_filepath)
        print('语料转词袋耗时 {:.2f}s'.format(time.time() - beg))

    def _split_word(self, sentence, stoplist=[]):
        words = jieba.cut(sentence)
        res = [i for i in words if i not in stoplist]
        return res

    def get_words(self, query : str):
        return self._split_word(query, self.stoplist)

    def interact(self, query : str):
        sentences = self._split_word(query, self.stoplist)  # 分词
        vec = self.dictionary.doc2bow(sentences)  # 转词袋表示
        print("**", vec, self.tfidf)

        print("idx_pth:: \n", self.index_pth)
        print("cur_pth::\n", os.getcwd())

        sims = self.index[self.tfidf[vec]]  # 相似度比较
        sorted_sims = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)  # 逆序

        print('分词结果 ->  ', sentences)
        print("相似度比较 ->  ", sorted_sims[:5])
        cnt = 0
        res = ''
        for i, similarity in sorted_sims[:5]:
            if cnt == 0:
                if similarity > 0.78:
                    res = self.data[str(i)]['answer']
                else:
                    res = 'answer not found'
                cnt = 1
            print(similarity, self.data[str(i)])
        return res


