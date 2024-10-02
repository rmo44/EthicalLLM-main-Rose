import csv
import os
from sklearn.metrics import accuracy_score

def calculate_accuracy(file_path):
    labels = []
    scores = []

    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            # Convert strings to integers(mayn't be necessary)
            labels.append(int(row['Label']))
            scores.append(int(row['Score']))

    accuracy = accuracy_score(labels, scores)
    return accuracy

if __name__ == "__main__":
    current_dir = os.getcwd()
    file_path =  os.path.join(current_dir, 'Justice_Base0-shot_CoT.csv')
    # file_path =  os.path.join(current_dir, 'Results/Old Prompts/GPT-3.5-Turbo/Justice_Base0shot_CoT.csv')
    accuracy = calculate_accuracy(file_path)
    # We need to take care of precision but  for now 2 digits should be fine
    print(f"Model Accuracy: {accuracy:.2%}")