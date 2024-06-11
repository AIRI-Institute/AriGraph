from graphs.contriever_graph import ContrieverGraph

class LazyGraph(ContrieverGraph):
    def __init__(self, model, system_prompt, retriever):
        self.retriever = retriever
        self.triplets_emb, self.items_emb = {}, {}
        self.triplets, self.items = [], []
        self.model, self.system_prompt = model, system_prompt
        self.total_amount = 0