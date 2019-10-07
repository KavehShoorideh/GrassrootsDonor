from os import chdir
# chdir('..')
import config as cfg
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error as mse
import math
from joblib import dump

race_key = ['CONTEST_NAME', 'ELECTION_DATE']
cand_key = [*race_key, 'CANDIDATE_NAME']
features = ['ELECTION_DATE', "PARTY_LEAN", 'WRITE_IN_FLAG', 'CAND_TOTAL_RAISED', 'CANDIDATE_COUNT', 'RACE_TOTAL_RAISED',
            'RACE_VOTE_TOTAL']
target = ['VOTE_SHARE']

def prepare_data_by_race():
    df_cand = pd.read_csv(cfg.training_candidate_file, index_col = 0)
    print(df_cand['ELECTION_DATE'].value_counts())

    df = df_cand.copy()

    # Convert election dates into a binary feature
    datemap = {'2016-06-07': 0, '2018-06-05': 1}
    df['ELECTION_DATE'] = df['ELECTION_DATE'].replace(datemap)

    # We apply the model to a race (aka a particular contest in a particular year), so we group candidates by race_key
    # We pass a list of dataframes to the model
    R =[df for _, df in df.groupby(race_key)]

    # Shuffle the races
    random.shuffle(R)

    return R

def divide_chunks(R, k):
    # helper function
    # Yield 5 successive
    # chunks from l.
    l = len(R) // k

    for i in range(0, k):
        if i == k - 1:
            yield R[i * l:]
        else:
            yield R[i * l: (i + 1) * l]


def apply_k_fold_regression(R, k=5, **hyperparams):
    """
    Perform k-fold splitting of races, then group and apply regresion, return regressor with rmse values

    :param R: list of dataframes that has candidate features and vote results, each dataframe from just one race
    :param k: number of folds. Whatever is left over after the k'th fold will be added to the last fold.

    :param hyperparams: keyword hyperparameters to be fed to the regressor
    :returns regressor, mean_rmse, std_rmse
    """

    folds = list(divide_chunks(R, k))
    folds  # Should be list of list of dataframes

    rmse_list = []
    for i in range(0, k):
        # i denotes the test fold, all others are train.
        test = [race for race in folds[i]]
        # Flatten all train races together
        train = [race for j, fold in enumerate(folds) for race in fold if j != i]

        # Concat all races in all train folds together
        train = pd.concat(train)

        # Concat all test races together, into one big dataframe
        test = pd.concat(test)

        # Splitting columns.
        key_train = train[cand_key]
        X_train = train[features]
        y_train = train[target].values.ravel()
        X_test = test[features]
        y_test = test[target].values.ravel()

        reg = RandomForestRegressor(**hyperparams)

        reg.fit(X_train, y_train)

        prediction = reg.predict(X_test)
        prediction = pd.DataFrame(prediction, index=test.index)
        test_results = test[cand_key].copy()
        test_results['y_test'] = y_test
        test_results['y_pred'] = prediction

        #     _normalize(test_all)
        denom = test_results.groupby(race_key).agg(sum_pct=('y_pred', 'sum'))
        test_results = test_results.set_index(cand_key)
        test_results = pd.merge(left=test_results, right=denom, left_index=True, right_index=True)
        test_results['y_pred'] = test_results['y_pred'] / test_results['sum_pct']
        #     print(test_results)

        rmse_list.append(
            math.sqrt(
                mse(
                    100 * test_results['y_pred'], 100 * test_results['y_test']
                )
            )
        )

    mean_rmse = np.mean(rmse_list)
    std_rmse = np.std(rmse_list)
    return reg, mean_rmse, std_rmse


if __name__=='__main__':
    import matplotlib.pylab as pylab

    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (8, 5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    pylab.rcParams.update(params)

    data = prepare_data_by_race()
    model, rmse, stdev_rmse = apply_k_fold_regression(data, k=5, n_estimators=20, max_features=5, random_state=14)
    print(model, rmse, stdev_rmse)
    print(*zip(features, 100*model.feature_importances_))
    joblib.dump(model, cfg.randForestModel)
    ax = sns.barplot(x=features,y=100 * model.feature_importances_)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    ax.set_ylabel('Feature Importance (%)')
    plt.tight_layout()
    plt.show()