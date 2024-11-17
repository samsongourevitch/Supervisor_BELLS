import openai
import json
import os
import argparse
from tqdm import tqdm
import pandas as pd
from supervisor import evaluate_safety
from utils import extract_input_output, jsonl_to_df

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def process_jsonl(input_file, output_file, dataset, debug_mode=False):
    """
    Process the input JSONL file, classify each entry, and write the results to the output JSONL file.
    """
    results = []
    with open(input_file, "r") as infile:
        for line in tqdm(infile):
            data = json.loads(line)
            input_text, output_text = extract_input_output(data, dataset=dataset)

            if input_text and output_text:
                classification = evaluate_safety(input_text, output_text, debug_mode=debug_mode)
                # Append the result with the classification
                results.append({
                    "dataset": data['dataset'],
                    "goal": data['extra']['goal'], 
                    "category": data['extra']['category'],
                    "jailbroken": data['extra']['jailbroken'],
                    "supervisor": "lenotre0",
                    "user_msg": input_text,
                    "assistant_msg": output_text,
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
    parser.add_argument("--input_file", type=str, help="Path to the input JSONL file.", default="metadata.jsonl")
    parser.add_argument("--output_file", type=str, help="Path to save the evaluation results.", default="evaluations.csv")
    parser.add_argument("--dataset", type=str, help="Dataset name.", default="jbb-JBC")
    parser.add_argument("--debug_mode", help="Enable debug mode.", default=True)
    args = parser.parse_args()

    # Input and output file paths
    input_file = "datasets/" + args.input_file
    output_file = "outputs/" + args.output_file

    print(f"Processing file: {input_file}")
    process_jsonl(input_file, output_file, args.dataset, args.debug_mode)
    print(f"Results saved to: {output_file}")

    # Load the data from the other supervisor as well as from ours into a DataFrame
    df_other_supervisors = jsonl_to_df(input_file, args.dataset)
    df_lenotre = pd.read_csv(output_file)

    # Merge the two DataFrames
    df_merged = pd.concat([df_other_supervisors, df_lenotre])

    # Save the merged DataFrame to a CSV file
    df_merged.to_csv('outputs/merged_evaluations', index=False)


if __name__ == "__main__":
    main()
