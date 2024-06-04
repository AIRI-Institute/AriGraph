from parent_graph import TripletGraph

class DummyGraph(TripletGraph):
    def __init__(self, model, system_prompt):
        super().__init__(model, system_prompt)
        
    def update(self):
        return []