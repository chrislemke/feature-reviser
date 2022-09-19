# -*- coding: utf-8 -*-
from typing import List, Tuple

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.feature_selection import chi2, f_classif, mutual_info_classif

from feature_reviser.utils import check_data


def revise_classifier(
    clf: BaseEstimator,
    X: pd.DataFrame,
    y: pd.Series,
    cat_features: List[str],
    num_features: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Examens the features of `X` for a provided classifier.
    It prints out different statistics and returns those as a tuple of dataframes.

    Args:
        clf (BaseEstimator): The classifier used for examine the features.
        df (pandas.DataFrame): The dataframe containing the categorical and numerical features.
        y (pandas.Series): The target variable.
        cat_features (List[str]): The list of categorical features.
        num_features (List[str]): The list of numerical features.

    Raises:
        TypeError: If the classifier does not contain the `fit` or the `feature_importances_ attribute.

    Returns:
        Tuple[pandas.DataFrame, pandas.DataFrame]: Tuple containing the result dataframes for categorical and numerical features.
    """

    check_data(X, y)

    cat_df = X[cat_features]
    num_df = X[num_features]

    if not hasattr(clf, "fit"):
        raise AttributeError("Classifier does not have fit method!")

    clf.fit(cat_df, y)
    if not hasattr(clf, "feature_importances_"):
        raise AttributeError("Classifier does not have feature_importances_ attribute!")
    cat_feature_importances = clf.feature_importances_

    clf.fit(num_df, y)
    if not hasattr(clf, "feature_importances_"):
        raise AttributeError("Classifier does not have feature_importances_ attribute!")
    num_feature_importances = clf.feature_importances_

    chi_2, chi2_p_value = chi2(cat_df, y)
    mi = mutual_info_classif(cat_df, y, discrete_features=True)
    f_statistic, f_classif_p_value = f_classif(num_df, y)
    num_corr = pd.concat([num_df, y], axis=1).corr(method="spearman").values[:-1, -1]

    result_cat_df = pd.DataFrame(
        [chi_2, chi2_p_value, mi, cat_feature_importances],
        columns=cat_df.columns,
        index=["chi_2", "p_value", "mutal_information", "feature_importance"],
    )
    results_num_df = pd.DataFrame(
        [f_statistic, f_classif_p_value, num_feature_importances, num_corr],
        columns=num_df.columns,
        index=["f_statistic", "p_value", "feature_importance", "correlation"],
    )

    print(result_cat_df)
    print(results_num_df)

    return result_cat_df, results_num_df
