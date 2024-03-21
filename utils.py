from copy import deepcopy

def process_triplets(raw_triplets):
    raw_triplets = raw_triplets.split(";")
    triplets = []
    for triplet in raw_triplets:
        if len(triplet.split(",")) > 3:
            continue
        elif len(triplet.split(",")) < 3:
            continue
        else:
            subj, relation, obj = triplet.split(",")
            subj, relation, obj = subj.strip(' \n"'), relation.strip(' \n"'), obj.strip(' \n"')
            if len(subj) == 0 or len(relation) == 0 or len(obj) == 0:
                continue
            triplets.append([subj, obj, {"label": relation}])
        
    return triplets

def parse_triplets_removing(text):
    text = text.split("[[")[-1]
    text = text.replace("[", "")
    text = text.strip("]")
    pairs = text.split("],")
    parsed_triplets = []
    for pair in pairs:
        splitted_pair = pair.split("->")
        if len(splitted_pair) != 2:
            continue
        first_triplet = splitted_pair[0].split(",")
        if len(first_triplet) != 3:
            continue
        subj, rel, obj = first_triplet[0].strip(''' '"\n'''), first_triplet[1].strip(''' '"\n'''), first_triplet[2].strip(''' '"\n''')
        parsed_triplets.append([subj, obj, {"label": rel}])
    return parsed_triplets

def parse_plan(plan):
    plan = plan.strip("[]").split(",")
    return [action.strip('''\n'" ''') for action in plan]

class Logger:
    def __init__(self, path):
        self.path = path
        
    def __call__(self, text):
        print(text)
        with open(self.path, "a") as file:
            file.write(text + "\n")
        
def remove_equals(graph):
    graph_copy = deepcopy(graph)
    for triplet in graph_copy:
        if graph.count(triplet) > 1:
            graph.remove(triplet)
    return graph 