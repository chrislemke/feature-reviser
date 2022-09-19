# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.feature_selection import SelectFromModel, SelectKBest, chi2, f_classif

from feature_reviser.utils import check_data


def select_with_classifier(
    clf: BaseEstimator,
    X: pd.DataFrame,
    y: pd.Series,
    select_k_best_first: bool = False,
    cat_features: Optional[List[str]] = None,
    num_features: Optional[List[str]] = None,
    cat_k_best: Optional[int] = None,
    num_k_best: Optional[int] = None,
    threshold: Optional[float] = None,
    max_features: Optional[int] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Optionally examens the features of `X` using `SelectKBest` for categorical and numerical features before the features of `X`
    are selected using `SelectFromModel` with the provided classifier.

    Args:
        clf (BaseEstimator): The classifier used for examine the features.
        X (pandas.DataFrame): The dataframe containing the categorical and numerical features.
        y (pandas.Series): The target variable.
        select_k_best_first (bool): If `True` the features are selected using `SelectKBest` first. Defaults to False.
        cat_features (Optional[List[str]]): The list of categorical features. Defaults to None. This is needed if `select_k_best_first` is `True`.
        num_features (Optional[List[str]]): The list of numerical features. Defaults to None. This is needed if `select_k_best_first` is `True`.
        cat_k_best (Optional[int]): The max number of categorical features to select using `SelectKBest`.
            Defaults to None. This is needed if `select_k_best_first` is `True`.
        num_k_best (Optional[int]): The max number of numerical features to select using `SelectKBest`.
            Defaults to None. This is needed if `select_k_best_first` is `True`.
        threshold (Optional[float]): The threshold used for `SelectFromModel`. Defaults to None.
        max_features (Optional[int]): The max number of features to select using `SelectFromModel`. Defaults to None.

    Raises:
        ValueError: If `select_k_best_first` is `True` and `cat_features`, `num_features`, `cat_k_best` or `num_k_best` are `None`.
        TypeError: If the classifier does not contain the `fit` attribute.

    Returns:
        Tuple[pandas.DataFrame, pandas.Series]: Tuple containing the selected features and the target variable.
    """
    check_data(X, y)

    if not hasattr(clf, "fit"):
        raise AttributeError("Classifier does not have fit method!")

    if select_k_best_first:

        if (
            cat_features is None
            or num_features is None
            or cat_k_best is None
            or num_k_best is None
        ):
            raise ValueError(
                "If `select_k_best_first` is set to `True`, `cat_features`, `num_features`, `cat_k_best`, and `num_k_best` must be provided!"
            )

        cat_df = X[cat_features]
        num_df = X[num_features]

        print("Selecting categorical features...")
        cat_transformer = SelectKBest(chi2, k=min(cat_k_best, cat_df.shape[1] - 1)).fit(
            cat_df, y
        )
        print("Selecting numerical features...")
        num_transformer = SelectKBest(
            f_classif, k=min(num_k_best, num_df.shape[1] - 1)
        ).fit(num_df, y)

        cat_x = cat_transformer.transform(cat_df)
        num_x = num_transformer.transform(num_df)

        columns = [
            cat_df.columns[i] for i in cat_transformer.get_support(indices=True)
        ] + [num_df.columns[i] for i in num_transformer.get_support(indices=True)]

        print(
            f"The following columns were selected using the `SelectKBest` algorithm: {columns}.".replace(
                "[", ""
            )
            .replace("]", "")
            .replace("'", "")
        )
        X = pd.DataFrame(data=np.column_stack((cat_x, num_x)), columns=columns)

    print("Selecting features with classifier...")

    selector = SelectFromModel(
        estimator=clf, threshold=threshold, max_features=max_features or X.shape[1]
    ).fit(X, y)
    selected = selector.transform(X)
    columns = [X.columns[i] for i in selector.get_support(indices=True)]
    print(
        f"The following columns were selected using the `{clf.__class__.__name__}`: {columns}.".replace(
            "[", ""
        )
        .replace("]", "")
        .replace("'", "")
    )
    return (
        pd.DataFrame(
            data=selected,
            columns=columns,
        ),
        y,
    )
