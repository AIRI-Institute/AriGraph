import sys

import torch

#First you need to download contriver repo:
# https://github.com/facebookresearch/contriever
# specify path to contriever repo:
# contriever_path = "/home/griver/projects/ml/nlp/contriever/"
# if contriever_path not in sys.path:
#     sys.path.append(contriever_path)

from transformers import AutoTokenizer
from src.contriever import Contriever


class Retriever:

    @staticmethod
    def load_embedder_and_tokenizer(device="cpu"):
        embedder = Contriever.from_pretrained("facebook/mcontriever").to(device)
        tokenizer = AutoTokenizer.from_pretrained("facebook/mcontriever")
        return embedder, tokenizer

    @staticmethod
    @torch.no_grad()
    def get_embeddings(list_of_strings, embedder, tokenizer):
        inputs = tokenizer(list_of_strings, padding=True, truncation=True, return_tensors="pt").to(embedder.device)
        embeds = embedder(**inputs)
        return embeds

    def __init__(self, device="cpu"):
        super().__init__()
        self.embedder, self.tokenizer = self.load_embedder_and_tokenizer(device)

    @torch.no_grad()
    def embed(self, list_of_str):
        """Returns embeddings of the input strings"""
        return self.get_embeddings(list_of_str, self.embedder, self.tokenizer)

    def search(
            self,
            key_strings,
            query_strings,
            topk: int=None,
            similarity_threshold: float=None,
            return_embeds=False,
            return_scores=False,
    ):
        """
        Finds most_similar key strings for each of query string and returns these strings and their indices
        If topk is specified returns top k closest results for each query.
        If similarity_threshold is specified returns results with similarity score higher than similarity_threshold.
        Only one of similarity_threshold and topk should be specified.

        :param key_embeds: list of embeddings
        :param query_embeds: list of embeddings
        :param topk: if not None, returns top k most similar results
        :param similarity_threshold: if not None, returns results with similarity scores higher than the threshold
        :param return_embeds: if True adds embeds to the output dict
        :param return_scores: if True adds similarity scores to the output dict,
        :return: dict(
            idx = list with indices of most similar embeddings (list of lists if there are several queries)
            strings = same as idx but with key_strings instead of indices
            embeds (optional) = same as idx but with embeddings of key_strings instead of indices
            scores (optional) = same as idx but with similarity scores instead of indices
        )
        """
        batch_request = True
        if isinstance(query_strings, str):
            batch_request = False
            query_strings = [query_strings]

        num_q = len(query_strings)

        key_embeds = self.embed(key_strings)
        query_embeds = self.embed(query_strings)
        result = self.search_in_embeds(
            key_embeds, query_embeds, topk, similarity_threshold, return_embeds, return_scores
        )

        result['strings'] = [[key_strings[k_id] for k_id in result['idx'][q_id] ] for q_id in range(num_q)]
        if not batch_request:
            result = {k: v[0] for k,v in result.items()}

        return result

    @staticmethod
    @torch.no_grad()
    def search_in_embeds(
        key_embeds,
        query_embeds,
        topk: int=None,
        similarity_threshold: float=None,
        return_embeds=False,
        return_scores=False,
    ):
        """
        Finds closest key_embeds for each of query_embeds and returns these embeddings and their indices
        If topk is specified returns top k closest results for each query.
        If similarity_threshold is specified returns results with similarity score higher than similarity_threshold.
        Only one of similarity_threshold and topk should be specified.

        :param key_embeds: list of embeddings
        :param query_embeds: list of embeddings
        :param topk: if not None, returns top k most similar results
        :param similarity_threshold: if not None, returns results with similarity scores higher than the threshold
        :param return_embeds: if True adds embeds to the output dict
        :param return_scores: if True adds similarity scores to the output dict

        :return: dict(
            idx = list with indices of most similar embeddings (list of lists if there are several queries)
            embeds (optional) = same as idx but with embeddings of key_strings instead of indices
            scores (optional) = same as idx but with similarity scores instead of indices
        )
        """
        if int(topk is None) + int(similarity_threshold is None) != 1:
            raise ValueError("You should specify either topk or similarity_threshold but not both!")

        scores = query_embeds  @ key_embeds.T # shape: (num_keys,) or (num_queries, num_keys)
        batch_request = len(query_embeds.shape) > 1

        if not batch_request:
            scores = scores.reshape(1, -1) # shape: (num_queries, num_keys)
        num_q = scores.shape[0]

        if topk:
            sorted_idx = scores.argsort(-1, descending=True)  # sort for each query
            selected_idx = sorted_idx[:,:topk]
            #selected_scores = scores.gather(1, index=selected_idx)
            selected_idx = selected_idx.tolist()
        else:
            selected_idx = [[] for i in range(num_q)]
            for (q_id, k_id) in (scores >= similarity_threshold).nonzero():
                selected_idx[q_id].append(k_id)

        result = dict(idx=selected_idx)

        if return_embeds:
            result['embeds'] = [
                 [key_embeds[k_id] for k_id in selected_idx[q_id]]
                 for q_id in range(num_q)
            ]
        if return_scores:
            result['scores'] = [
                 [scores[q_id, k_id] for k_id in selected_idx[q_id]]
                 for q_id in range(num_q)
            ]
        if not batch_request:
            result = {k: v[0] for k,v in result.items()}

        return result


if __name__ == "__main__":
    graph_test = {
        'items': ['toothbrush', 'dirty plate', 'fantasy book', 'elegant table runner', 'business suit', 'sleeping lamp',
                  'toy car', 'wet towel', 'dumbbell', 'swimming fins', 'raw meat'],
        'graph': ['dining room, contains, dining table', 'dining table, has on, toothbrush',
                  'dining table, has on, centerpiece', 'dining table, has on, candles',
                  'dining table, has on, salt and pepper shakers', 'dining room, has exit, east',
                  'dining room, has exit, north', 'dining room, has exit, south', 'dining room, has exit, west',
                  'kitchen, contains, dishwasher', 'kitchen, contains, refrigerator', 'kitchen, contains, cook table',
                  'dishwasher, is, closed', 'refrigerator, is, closed', 'cook table, has on, business suit',
                  'kitchen, has exit, east', 'kitchen, has exit, north', 'kitchen, has exit, south',
                  'kitchen, is west of, dining room', 'dining room, is east of, kitchen', 'bathroom, contains, toilet',
                  'toilet, has on, toilet paper', 'toilet paper, is on, toilet', 'toilet, has on, sleeping lamp',
                  'sleeping lamp, is on, toilet', 'bathroom, contains, sink', 'sink, has on, deodorant',
                  'deodorant, is on, sink', 'bathroom, contains, towel rack', 'towel rack, is, empty',
                  'bathroom, has exit, east', 'bathroom, has exit, south', 'bathroom, contains, table runner',
                  'table runner, is on, floor', 'bathroom, is north of, kitchen', 'kitchen, is south of, bathroom',
                  'kids room, contains, toy storage cabinet', 'kids room, contains, study table',
                  'kids room, contains, kids bed', 'study table, has on, school notebooks',
                  'study table, has on, felt tip pens', 'study table, has on, dumbbell',
                  'kids bed, has on, dirty plate', 'kids room, has exit, east', 'kids room, has exit, south',
                  'kids room, has exit, west', 'kids room, is east of, bathroom', 'bathroom, is west of, kids room',
                  'living room, contains, tv table', 'tv table, has on, tv', 'living room, contains, sofa',
                  'sofa, has on, raw meat', 'sofa, has on, decorative pillow',
                  'living room, contains, game console cabinet', 'game console cabinet, has in, gaming console',
                  'living room, has exit, south', 'living room, has exit, west', 'living room, is east of, kids room',
                  'kids room, is west of, living room', 'master bedroom, contains, wardrobe',
                  'master bedroom, contains, king size bed', 'king size bed, has on, wet towel',
                  'master bedroom, contains, bedside table', 'bedside table, has on, alarm clock',
                  'bedside table, has on, bed lamp', 'master bedroom, has exit, north',
                  'master bedroom, has exit, south', 'master bedroom, has exit, west',
                  'master bedroom, is south of, living room', 'living room, is north of, master bedroom',
                  'library, has odor, bad odor', 'library, contains, bookcase', 'bookcase, has on, detective book',
                  'library, contains, reading table', 'reading table, has on, swimming fins',
                  'reading table, has on, reading glasses', 'library, has exit, north', 'library, has exit, west',
                  'library, is south of, master bedroom', 'master bedroom, is north of, library',
                  'swimming pool area, contains, pool equipment rack',
                  'swimming pool area, contains, table for pool chemicals', 'swimming pool area, contains, toy car',
                  'swimming pool area, has exit, east', 'swimming pool area, has exit, north',
                  'swimming pool area, has exit, west', 'pool equipment rack, has on, swimming goggles',
                  'pool equipment rack, has on, life ring', 'table for pool chemicals, has on, chlorine',
                  'toy car, is on, floor', 'swimming pool area, is west of, library',
                  'library, is east of, swimming pool area', 'gym, contains, sport equipment locker',
                  'gym, contains, empty dumbbell stand', 'gym, contains, empty treadmill', 'fantasy book, is on, floor',
                  'gym, has exit, east', 'gym, has exit, north', 'gym, is west of, swimming pool area',
                  'swimming pool area, is east of, gym']
    }

    contriever = Retriever("cpu")
    print("<< SEARCH WITH MULTIPLE QUERIES >>")
    results = contriever.search(
        key_strings=graph_test['graph'],
        query_strings=graph_test['items'],
        similarity_threshold=0.9, return_scores=True
    )

    for i, query in enumerate(graph_test['items']):
        print('==='*15)
        print(f"#{i} SEARCH FOR ITEM: {query}")
        print("RESULTS:")
        for triplet, similarity in zip(results['strings'][i], results['scores'][i]):
            print(f"{similarity:.3f}: {triplet}")
    print("\n\n\n")

    print("<< SEARCH WITH SINGLE QUERY >>")
    query = "sleeping lamp" #elegant table runner
    results = contriever.search(
        key_strings=graph_test['graph'],
        query_strings=query,
        topk=5, return_scores=True
    )

    print('===' * 15)
    print(f"#SEARCH FOR ITEM: {query}")
    print("RESULTS (for topk results are sorted by similarity):")
    for triplet, similarity in zip(results['strings'], results['scores']):
        print(f"{similarity:.3f}: {triplet}")
    print("\n\n\n")

    print("<< SEARCH WITHOUT RECOMPUTING EMBEDDINGS: >>")
    #Get embeddings directly:
    query = 'elegant table runner'
    triplet_embeds = contriever.embed(graph_test['graph'])
    query_embeds = contriever.embed([query])[0]
    indices = contriever.search_in_embeds(triplet_embeds, query_embeds, topk=4)['idx']
    print('===' * 15)
    print(f"#SEARCH FOR ITEM: {query}")
    print("RESULTS (for topk results are sorted by similarity):")
    for top_i, idx in enumerate(indices):
        print(top_i, graph_test['graph'][idx])