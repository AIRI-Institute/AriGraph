import numpy as np
import matplotlib.pyplot as plt

file = "interactive_logs_expanding_replacing_clean_3x3.txt"
with open(file, "r") as f:
    text = f.readlines()
    
precision = []
recall = []

for i in range(len(text)):
    if text[i].startswith("Precision: "):
        precision.append(float(text[i].split("Precision: ")[-1]))
        recall.append(float(text[i + 1].split("Recall:")[-1]))

plt.plot(precision, label = "Precision")
plt.plot(np.array(recall) / max(recall), label = "Recall")
plt.legend()
plt.show()
plt.savefig("Precision_recall_expanding_replacing.pdf")