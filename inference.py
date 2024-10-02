import csv
import time
import os
import pandas as pd
from models.openai_models import query_openai, query_gpt2
from models.llama import query_ollama2, query_ollama3
from models.mistral import query_mistral
from models.google_gemini import query_gemini
from models.bert import query_bert
from models.roberta import query_roberta_large
from prompts import generate_prompt
import argparse

def get_last_processed_id(output_file):
    if not os.path.exists(output_file):
        return 0
    
    df = pd.read_csv(output_file)
    if df.empty:
        return 0
    return df['ID'].max()

def process_csv(technique, input_file, output_file, output_file_combined, theory, model):
    results = []
    results_combined = []
    
    df = pd.read_csv(input_file, encoding='ISO-8859-1')
    df = df.head(2)

    # Ensure there's an 'id' column (There isn't. So, we create every time)
    if 'id' not in df.columns:
        df['id'] = range(1, len(df) + 1)
    
    # Get the last processed ID using our output file (eg. gpt2_Justice.csv)
    last_processed_id = get_last_processed_id(output_file)
    print(f"Resuming from ID: {last_processed_id + 1}")
    
    for index, row in df.iterrows():
        if row['id'] <= last_processed_id:
            continue
        
        if theory == 'Commonsense':
            label = row['label']
            scenario = row['input']
        elif theory == 'Justice':
            label = row['label']
            scenario = row['scenario']
        elif theory == 'Virtue':
            pass
        elif theory == 'Utilitarianism':
            pass
        elif theory == 'Deontology':
            pass

        # Generate the prompt
        prompt = generate_prompt(technique, scenario, theory)

        if model == "llama2":
            full_response, score, justification = query_ollama2(prompt)
        elif model == "llama3.1":
            full_response, score, justification = query_ollama3(prompt)
        elif model == "gemini":
            full_response, score, justification = query_gemini(prompt)
        elif model == "openai":
            full_response, score, justification = query_openai(prompt)
        elif model == "gpt2":
            full_response, score, justification = query_gpt2(prompt)
        elif model == "mistral":
            full_response, score, justification = query_mistral(prompt)
        elif model == "bert":
            full_response, score, justification = query_bert(prompt)
        elif model == "roberta":
            full_response, score, justification = query_roberta_large(prompt)
        else:
            raise ValueError(f"Unknown model: {model}")

        if full_response:
            result = {
                'ID': row['id'],
                'Label': label,
                'Scenario': scenario,
                technique: score,
                'Justification': justification,
                'Full Response': full_response
            }
            results.append(result)

            result_combined = {
                'ID': row['id'],
                'Label': label,
                'Scenario': scenario,
                technique: score,
                f'{technique}_Justification': justification,
            }
            results_combined.append(result_combined)
            
            # Write results immediately to avoid data loss in case of interruption(And we have now code to resume from whereever we want)
            write_results(output_file, [result], ['ID', 'Label', 'Scenario', technique, 'Justification', 'Full Response'])
            write_results(output_file_combined, [result_combined], ['ID', 'Label', 'Scenario', technique, f'{technique}_Justification'])
        
        # Adding sleep to avoid rate limiting if any (usually persistent for the gemini models) 
        # Only use it for gemini models (no need for other models)
        time.sleep(1)

    # Sanity check at the end to make sure we had the right prompt
    print(f"PROMPT WAS: {prompt}")
    return results

def write_results(file_path, results, fieldnames):
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for result in results:
            writer.writerow(result)

def main():
    theories = ['Commonsense', 'Justice', 'Virtue', 'Utilitarianism', 'Deontology']
    theory = theories[0]

    # Creating a parser to get the argument from command-line
    parser = argparse.ArgumentParser()

    # Defaulting to Base0-shot if not provided explicitly
    # Base0-shot, Base0-shot_CoT
    parser.add_argument('--technique', type=str, default='Base0-shot', help='Prompting technique you want to use')

    # llama2, llama3, gpt2, gemini, openai, mistral
    parser.add_argument('--model', type=str, default='llama2', help='Model you want to use')

    args = parser.parse_args()
    technique = args.technique
    model = args.model

    # Get the current directory
    current_dir = os.getcwd()
    # input_file = os.path.join(current_dir, 'Ethics/justice/justice_train.csv')
    input_file = os.path.join(current_dir, 'Ethics/commonsense/cm_train.csv')

    # Automatic naming conventions e.g., Justice_CoT.csv
    output_file = os.path.join(current_dir, f'{model}_{theory}_{technique}.csv')
    output_file_combined = os.path.join(current_dir, f'{model}_{theory}.csv')

    # Calling the process_csv function 
    process_csv(technique, input_file, output_file, output_file_combined, theory, model)

    # Sanity check
    print(f"Results were saved to {output_file} and {output_file_combined}")

if __name__ == "__main__":
    main()