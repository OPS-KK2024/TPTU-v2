import time
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import json
import re


CENTURIO_API_DELIMITER = '：'


def parse_api(api_line, delimiter):
    api_line = api_line.strip()
    assert api_line.count(delimiter) == 1
    name, description = api_line.split(delimiter)
    return name.strip(), description.strip()


def process_retrieval_ducoment_sensecenturio(documents_df):
    ir_corpus = {}
    corpus2tool = {}
    for row in documents_df.itertuples():
        doc = json.loads(row.document_content)
        ir_corpus[row.docid] = doc
        corpus2tool[doc] = parse_api(doc, delimiter=CENTURIO_API_DELIMITER)[0]
        # doc = json.loads(row.document_content)
        # ir_corpus[row.docid] = (doc.get('category_name', '') or '') + ', ' + \
        # (doc.get('tool_name', '') or '') + ', ' + \
        # (doc.get('api_name', '') or '') + ', ' + \
        # (doc.get('api_description', '') or '') + \
        # ', required_params: ' + json.dumps(doc.get('required_parameters', '')) + \
        # ', optional_params: ' + json.dumps(doc.get('optional_parameters', '')) + \
        # ', return_schema: ' + json.dumps(doc.get('template_response', ''))
        # corpus2tool[(doc.get('category_name', '') or '') + ', ' + \
        # (doc.get('tool_name', '') or '') + ', ' + \
        # (doc.get('api_name', '') or '') + ', ' + \
        # (doc.get('api_description', '') or '') + \
        # ', required_params: ' + json.dumps(doc.get('required_parameters', '')) + \
        # ', optional_params: ' + json.dumps(doc.get('optional_parameters', '')) + \
        # ', return_schema: ' + json.dumps(doc.get('template_response', ''))] = doc['category_name'] + '\t' + doc['tool_name'] + '\t' + doc['api_name']
    return ir_corpus, corpus2tool

    
def process_retrieval_ducoment_sensecenturio_dedup(documents_df, \
    dedup=True, \
    dedup_funs=[(lambda x: x.replace(',', '，')), \
        (lambda x: (x.replace('多个档案进行合', '多个档案进行合并。') if '全息档案-检索结果：' in x and not x.endswith('多个档案进行合并。') else x))], \
    ):
    ir_corpus = {}
    corpus2tool = {}
    for row in documents_df.itertuples():
        doc = json.loads(row.document_content)
        if dedup:
            for fun in dedup_funs:
                doc = fun(doc)
        ir_corpus[row.docid] = doc
        corpus2tool[doc] = parse_api(doc, delimiter=CENTURIO_API_DELIMITER)[0]
    return ir_corpus, corpus2tool




class ToolRetriever:
    def __init__(self, corpus_tsv_path = "", model_path=""):
        self.corpus_tsv_path = corpus_tsv_path
        self.model_path = model_path
        self.corpus, self.corpus2tool, self.corpus_ids = self.build_retrieval_corpus()
        self.embedder = self.build_retrieval_embedder()
        self.corpus_embeddings = self.build_corpus_embeddings()
        
    def build_retrieval_corpus(self):
        print("Building corpus...")
        documents_df = pd.read_csv(self.corpus_tsv_path, sep='\t')
        # corpus, corpus2tool = process_retrieval_ducoment(documents_df)
        # corpus, corpus2tool = process_retrieval_ducoment_sensecenturio(documents_df)
        corpus, corpus2tool = process_retrieval_ducoment_sensecenturio_dedup(documents_df)
        corpus_ids = list(corpus.keys())
        corpus = [corpus[cid] for cid in corpus_ids]
        return corpus, corpus2tool, corpus_ids

    def build_retrieval_embedder(self):
        print("Building embedder...")
        embedder = SentenceTransformer(self.model_path)
        return embedder
    
    def build_corpus_embeddings(self):
        print("Building corpus embeddings with embedder...")
        corpus_embeddings = self.embedder.encode(self.corpus, convert_to_tensor=True)
        return corpus_embeddings

    def retrieving(self, query, top_k=5, excluded_tools={}):
        print("Retrieving...")
        start = time.time()
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.corpus_embeddings, top_k=10*top_k, score_function=util.cos_sim)
        retrieved_tools = []
        for rank, hit in enumerate(hits[0]):
            tool_name = self.corpus2tool[self.corpus[hit['corpus_id']]]
            if tool_name in excluded_tools:
                top_k += 1
                continue
            tmp_dict = {
                "doc_id": self.corpus_ids[hit['corpus_id']],
                "doc": self.corpus[hit['corpus_id']],
                "tool_name": tool_name,
                "score": hit['score'],
            }
            ###########################################################################################
            # category, tool_name, api_name = self.corpus2tool[self.corpus[hit['corpus_id']]].split('\t') 
            # category = standardize_category(category)
            # tool_name = standardize(tool_name) # standardizing
            # api_name = change_name(standardize(api_name)) # standardizing
            # if category in excluded_tools:
            #     if tool_name in excluded_tools[category]:
            #         top_k += 1
            #         continue
            # tmp_dict = {
            #     "category": category,
            #     "tool_name": tool_name,
            #     "api_name": api_name
            # }
            ###########################################################################################
            retrieved_tools.append(tmp_dict)
        return retrieved_tools

