from sklearn.metrics import accuracy_score, recall_score, precision_score
import pandas as pd
import matplotlib.pyplot as plt
from utils import jsonl_to_df
import seaborn as sns
import argparse

sns.set_theme()


def compute_clf_metrics(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    return accuracy, recall, precision


def assess_supervisor_perf(df, dataset):
    if dataset == 'jbb-JBC':
        y_true =  df['jailbroken']
    elif dataset == 'traces_unrealistic':
        y_true = df['is_hallucination']
    else:
        raise NotImplementedError('Dataset not supported')
    
    y_pred = df['classification']
    accuracy, recall, precision = compute_clf_metrics(y_true, y_pred)
    return pd.Series({'accuracy': accuracy, 'recall': recall, 'precision': precision})


def compare_supervisor_perf(df_name, dataset):
    df = pd.read_csv(df_name)
    perfs = df.groupby('supervisor').apply(assess_supervisor_perf, dataset)
    # three bar plot: accuracy, recall, precision
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))
    cats = perfs.columns
    colors = ['skyblue', 'salmon', 'lightgreen']
    for i, cat in enumerate(cats):
        ax = axs[i]
        perfs[cat].plot(kind='barh', ax=ax, color=colors[i])
        ax.set_xlim(0, 1)
        ax.set_title(cat.capitalize())
    plt.suptitle(f'Supervisor Performance on dataset {dataset}')
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Compare supervisor performance')
    parser.add_argument('--file_path', type=str, help='Path to the csv file')
    parser.add_argument('--dataset', type=str, help='Dataset to evaluate')
    args = parser.parse_args()
    compare_supervisor_perf(args.file_path, args.dataset)

if __name__ == '__main__':
    main()