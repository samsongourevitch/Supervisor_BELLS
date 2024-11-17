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


def process_jsonl(input_file, output_file, dataset, debug_mode, version):
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
                    classification = evaluate_safety(system_msg, user_msg, assistant_msg, version=version, debug_mode=debug_mode)
                    classification = classification.strip("'\"").lower()
                    if classification == "no failure":
                        classification = False
                    elif classification == "failure":
                        classification = True
                    else:
                        classification = None
                    # Append the result with the classification
                    results.append({
                        "dataset": data['dataset'],
                        "goal": data['extra']['goal'], 
                        "category": data['extra']['category'],
                        "jailbroken": data['extra']['jailbroken'],
                        "supervisor": "lenotre0",
                        "system_msg": system_msg,
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
                    classification = evaluate_safety(system_msg, user_msg, assistant_msg, version=version, debug_mode=debug_mode)
                    if classification == "no failure":
                        classification = False
                    else:
                        classification = True
                    # Append the result with the classification
                    results.append({
                        "dataset": data['dataset'],
                        "is_hallucination": data["calls"][0]["extra"]["is_hallucination"],
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
    parser.add_argument("--version", type=int, help="Version of the evaluation prompt to use.", default=0)
    parser.add_argument("--merge", type=str, help="Merge with the other supervisors.", default="False")
    parser.add_argument("--debug_mode", type=str, help="Enable debug mode.", default="True")
    args = parser.parse_args()

    if args.debug_mode.lower() == "true":
        args.debug_mode = True
    elif args.debug_mode.lower() == "false":
        args.debug_mode = False
    else:
        raise ValueError("Invalid value for debug_mode. Please use 'True' or 'False'.")

    if args.merge.lower() == "true":
        args.merge = True
    elif args.merge.lower() == "false":
        args.merge = False
    else:
        raise ValueError("Invalid value for merge. Please use 'True' or 'False'.")

    # Input and output file paths
    input_file = "datasets/" + args.input_file + ".jsonl"
    # add day and time to the output file name
    output_file = "outputs/" + "evaluation_" + args.input_file + "_" + time.strftime("%m%d-%H%M") + ".csv"

    print(f"Processing file: {input_file}")
    process_jsonl(input_file, output_file, args.input_file, args.debug_mode, args.version)
    print(f"Results saved to: {output_file}")

    if args.merge:
        print("Merging with other supervisors...")
        df_supervisors = jsonl_to_df(input_file, args.input_file)
        df_merged = pd.concat([pd.read_csv(output_file), df_supervisors])
        output_file_merged = "outputs/" + "evaluation_merged_" + args.input_file + "_" + time.strftime("%m%d-%H%M") + ".csv"
        df_merged.to_csv(output_file_merged, index=False)
        print(f"Merged results saved to: {output_file_merged}")
        print("run python src/visualization.py --file_path " + output_file_merged + "--dataset " + args.dataset + " to compare the performance of different supervisors")

if __name__ == "__main__":
    main()
