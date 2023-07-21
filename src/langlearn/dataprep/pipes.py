import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder, StandardScaler

def sklearn_pipe(df: pd.DataFrame, 
                 verbose: bool=False, 
                 categorical_cols: list=None,
                 ordinal_cols: list=None, 
                 numerical_cols: list=None) -> Pipeline:
    """Build a sklearn Pipeline."""
    
    # categorical columns
    if not categorical_cols:
        categorical_cols = [col for col in df.select_dtypes('category').columns if not df[col].cat.ordered]
    print(f"Categorical columns are: {categorical_cols}")
    categorical_pipe = Pipeline([  # noqa: F841
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        #('selector', SelectPercentile(chi2, percentile=50)),
    ], verbose=verbose)

    # ordinal columns
    if not ordinal_cols:
        ordinal_cols = [col for col in df.select_dtypes('category').columns if df[col].cat.ordered]
    print(f"Ordinal columns are: {ordinal_cols}")
    ordinal_pipe = Pipeline([  # noqa: F841
        ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)),
        #('selector', SelectPercentile(chi2, percentile=50)),
    ], verbose=verbose)

    # numerical columns
    if not numerical_cols:
        numerical_cols = list(df.select_dtypes('number').columns)
    print(f"Numerical columns are: {numerical_cols}")
    numeric_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy="median")),
        #('scaler', StandardScaler()),
        ('scaler', MinMaxScaler()),
        #('selector', VarianceThreshold())
    ], verbose=verbose)

    # combine numerical and categorical processing
    cols_pipe = ColumnTransformer([
        ('cat', categorical_pipe, categorical_cols),
        ('ord', ordinal_pipe, ordinal_cols),
        ('num', numeric_pipe, numerical_cols),
    ], verbose=verbose)
    cols_pipe.set_output(transform='pandas')

    return cols_pipe


# ruff: noqa: E501