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
            system_msg = None
            user_msg = entry["calls"][0]["messages"][0]["content"]
            assistant_msg = entry["calls"][0]["messages"][1]["content"]
            return system_msg, user_msg, assistant_msg
        except (KeyError, IndexError) as e:
            print(f"Error extracting input/output: {e}")
            return None, None
    elif dataset == "traces_unrealistic":
        try:
            system_msg = entry["calls"][0]["messages"][0]["content"]
            user_msg = entry["calls"][0]["messages"][1]["content"]
            assistant_msg = entry["calls"][0]["messages"][2]["content"]
            return system_msg, user_msg, assistant_msg
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
                        'dataset': record['dataset'],
                        'goal': goal,
                        'category': category,
                        'jailbroken': jailbroken,
                        'supervisor': supervisor,
                        'system_msg': None,
                        'user_msg': user_msg,
                        'assistant_msg': assistant_msg,
                        'classification': jailbreak,
                    })

    elif dataset == "traces_unrealistic":
        # Read the JSONL file line by line
        with open(file_path, 'r') as f:
            for line in f:
                record = json.loads(line.strip())  # Parse JSON object
                failure_types = record['failure_types']
                extra_evaluations = record['extra']['evaluations']
                hallucination_flags = {
                    key: value['hallucination']
                    for key, value in extra_evaluations.items()
                    if 'hallucination' in value
                }
                is_hallucination = record['calls'][0]['extra']['is_hallucination']

                # Extract user and assistant messages from 'calls' section
                system_msg = record['calls'][0]['messages'][0]['content']
                user_msg = record['calls'][0]['messages'][1]['content']
                assistant_msg = record['calls'][0]['messages'][2]['content']

                for supervisor, hallucination in hallucination_flags.items():
                    # Normalize hallucination flags
                    if isinstance(hallucination, (int, float)):
                        hallucination = hallucination > 0.5
                    elif isinstance(hallucination, str):
                        hallucination = hallucination.lower() in ["true", "yes"]
                    
                    data.append({
                        'dataset': record['dataset'],
                        'is_hallucination': is_hallucination,
                        'supervisor': supervisor,
                        'system_msg': system_msg,
                        'user_msg': user_msg,
                        'assistant_msg': assistant_msg,
                        'classification': hallucination,
                    })

    else:
        print(f"Dataset {dataset} not recognized.")
        raise NotImplementedError

    # Create a DataFrame from the data list
    df = pd.DataFrame(data)
    return df