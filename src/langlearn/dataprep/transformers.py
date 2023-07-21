import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import normalize


class SpacyDocsPreprocessor(TransformerMixin, BaseEstimator):
  def __init__(self, docs: dict, token_attribute: str="text"):
    # A dict of {doc_id: spacy.Doc, ...}
    self.docs = docs
    # token.text, token.lemma_, token.pos_, token.morph, token.dep_
    self.token_attribute = token_attribute

  def fit(self, X, y=None):
    return self

  def transform(self, X):
    _mydocs = list()
    for doc_id in X:
      doc = self.docs[doc_id]
      if self.token_attribute:
        _mydocs.append([getattr(token, self.token_attribute) for token in doc])
      else:
        _mydocs.append(token for token in doc)
    return _mydocs
  
  def get_feature_names_out(self, input_features=None):
    if input_features is None:
      input_features = []
    feature_names = list(input_features)
    return np.asarray(feature_names, dtype=object)
  

class GroupNormalizer(TransformerMixin, BaseEstimator):
    def __init__(self, group_name=None, norm: str='l1'):
        self.group_name = group_name
        self.norm = norm  # norm{‘l1’, ‘l2’, ‘max’}
        self.feature_names_out = []
        
    def fit(self, X: pd.DataFrame, y=None):
      print(f"GN.fit: {X.shape}")
      if not self.group_name:
        self.group_name = X.columns[0]
        print(self.group_name)
      return self
    
    def transform(self, X: pd.DataFrame):
        print(f"GN.transform: {X.shape}")
        
        # columns to scale
        numerical_cols = X.select_dtypes('number').columns
        #print(numerical_cols)
        _df = pd.DataFrame(columns=[self.group_name]+list(numerical_cols))
        _df[self.group_name] = X[self.group_name].cat.remove_unused_categories()
        _df[numerical_cols] = X[numerical_cols].copy()
        groups = _df.groupby(self.group_name, sort=False)[numerical_cols]
        ##print(groups)

        for group in groups.indices:
            #print(groups.get_group(group))
            normalized = normalize(
               groups.get_group(group).fillna(-1), norm=self.norm, axis=0, copy=True)
            #print(normalized.shape)
            #print(group)
            _df.iloc[groups.indices[group], 1:] = normalized

        _df.drop(columns=self.group_name, inplace=True)
        _df.rename(columns=lambda x: x+'_scaled', inplace=True)
        self.feature_names_out = list(_df.columns)
        print(f"...GN.transformed: {_df.shape}")
        return _df
          
    def get_feature_names_out(self, input_features=None):
        feature_names = self.feature_names_out
        # print("lem_out:"+str(feature_names))
        return np.asarray(feature_names, dtype=object)
