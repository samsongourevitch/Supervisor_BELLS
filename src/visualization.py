from sklearn.metrics import accuracy_score, recall_score, precision_score
import pandas as pd
import matplotlib.pyplot as plt


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


def compare_supervisor_perf(df, dataset):
    perfs = df.groupby('supervisor').apply(assess_supervisor_perf, dataset)
    # three bar plot: accuracy, recall, precision
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    perfs.plot(kind='bar', ax=axs)
    axs[0].set_title('Accuracy')
    axs[1].set_title('Recall')
    axs[2].set_title('Precision')
    plt.suptitle(f'Supervisor Performance on dataset {dataset}')
    plt.show()