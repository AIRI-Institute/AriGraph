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

