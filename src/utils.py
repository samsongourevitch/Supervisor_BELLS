import json
import pandas as pd
from tqdm import tqdm

def extract_input_output(entry, dataset="jbb-JBC"):
    """
    Extracts the input and output content from a given JSON entry.
    Returns a tuple (input_text, output_text).
    """

    if dataset == "jbb-JBC":
        try:
            input_text = entry["calls"][0]["messages"][0]["content"]
            output_text = entry["calls"][0]["messages"][1]["content"]
            return input_text, output_text
        except (KeyError, IndexError) as e:
            print(f"Error extracting input/output: {e}")
            return None, None
    else:
        print(f"Dataset {dataset} not recognized.")
        raise NotImplementedError


def jsonl_to_df(file_path, dataset="jbb-JBC"):
    # Initialize a list to store processed data
    data = []

    if dataset == "jbb-JBC":
        # Read the JSONL file line by line
        with open(file_path, 'r') as f:
            for line in f:
                record = json.loads(line.strip())  # Parse JSON object
                goal = record['extra']['goal']
                category = record['extra']['category']
                evaluations = record['extra']['evaluations']
                jailbroken = record['extra']['jailbroken']

                # Extract user and assistant messages from 'calls' section
                user_msg = record['calls'][0]['messages'][0]['content']
                assistant_msg = record['calls'][0]['messages'][1]['content']

                # Iterate over evaluations
                for eval in evaluations:
                    supervisor = eval
                    jailbreak = evaluations[eval]['jailbreak']
                    if isinstance(jailbreak, int):
                        jailbreak = bool(jailbreak)
                    elif isinstance(jailbreak, float):
                        jailbreak = jailbreak > 0.5 # DISCUTABLE

                    data.append({
                        'goal': goal,
                        'category': category,
                        'jailbroken': jailbroken,
                        'supervisor': supervisor,
                        'user_msg': user_msg,
                        'assistant_msg': assistant_msg,
                        'classification': jailbreak
                    })
    else:
        print(f"Dataset {dataset} not recognized.")
        raise NotImplementedError

    # Create a DataFrame from the data list
    df = pd.DataFrame(data)
    return df