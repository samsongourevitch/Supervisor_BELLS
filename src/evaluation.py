import openai
import json
import os
import argparse
from tqdm import tqdm
import pandas as pd
from supervisor import evaluate_safety
from utils import extract_input_output, jsonl_to_df
import time

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def process_jsonl(input_file, output_file, dataset, debug_mode=False):
    """
    Process the input JSONL file, classify each entry, and write the results to the output JSONL file.
    """
    results = []

    if dataset == "jbb-JBC":
        with open(input_file, "r") as infile:
            for line in tqdm(infile):
                data = json.loads(line)
                system_msg, user_msg, assistant_msg = extract_input_output(data, dataset=dataset)

                if user_msg and assistant_msg:
                    classification = evaluate_safety(system_msg, user_msg, assistant_msg, dataset=dataset, debug_mode=debug_mode)
                    # Append the result with the classification
                    results.append({
                        "dataset": data['dataset'],
                        "goal": data['extra']['goal'], 
                        "category": data['extra']['category'],
                        "jailbroken": data['extra']['jailbroken'],
                        "supervisor": "lenotre0",
                        "user_msg": user_msg,
                        "assistant_msg": assistant_msg,
                        "classification": classification
                    })
    elif dataset == "traces_unrealistic":
        with open(input_file, "r") as infile:
            for line in tqdm(infile):
                data = json.loads(line)
                system_msg, user_msg, assistant_msg = extract_input_output(data, dataset=dataset)

                if user_msg and assistant_msg:
                    classification = evaluate_safety(system_msg, user_msg, assistant_msg, dataset=dataset, debug_mode=debug_mode)
                    # Append the result with the classification
                    results.append({
                        "dataset": data['dataset'],
                        "is_hallucination": data['extra']['is_hallucination'],
                        'supervisor': 'lenotre0',
                        "system_msg": system_msg,
                        "user_msg": user_msg,
                        "assistant_msg": assistant_msg,
                        "classification": classification
                    })

    # Write the results to the output file in a csv format
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)

def main():
    """
    Main function to process the JSONL file for safety classification.
    """

    # Argument parsing
    parser = argparse.ArgumentParser(description="Evaluate model responses to harmful prompts.")
    parser.add_argument("--input_file", type=str, help="Name of the file of the input JSONL file.", default="jbb-JBC")
    parser.add_argument("--debug_mode", help="Enable debug mode.", default=True)
    args = parser.parse_args()

    # Input and output file paths
    input_file = "datasets/" + args.input_file + ".jsonl"
    # add day and time to the output file name
    output_file = "outputs/" + "evaluation_" + args.input_file + "_" + time.strftime("%m%d-%H%M") + ".csv"

    print(f"Processing file: {input_file}")
    process_jsonl(input_file, output_file, args.input_file, args.debug_mode)
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
