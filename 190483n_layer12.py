# -*- coding: utf-8 -*-
"""190483N_Layer12.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1APEAfFsqyw9hMNjR8fAMlXj7lTxsaxXD

Importing all the Libraries that are needed
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series

from sklearn.utils import class_weight
from sklearn import svm
from sklearn import metrics
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.feature_selection import SelectKBest, f_classif, chi2
import numpy as np

#Reading all datasets available

train_set = pd.read_csv('/content/drive/MyDrive/ML/Layer12/train.csv')
test_set = pd.read_csv('/content/drive/MyDrive/ML/Layer12/test.csv')
valid_set = pd.read_csv('/content/drive/MyDrive/ML/Layer12/valid.csv')

train_set.head()

#Checking whether there are coloumns with missing values
null_val_cols = train_set.columns[train_set.isnull().any()]

for col in null_val_cols:
    print(col)

#Removing rows with unavailable values in label_2 in both train and valid data sets

train_set = train_set.dropna(subset=['label_2'])
valid_set = valid_set.dropna(subset=['label_2'])
train_set.head()

#Formating the datasets in the way we want. Features and labelts are being seperated and done seperately for both Train and valid sets
classifier = SVC()

X = pd.DataFrame(train_set.iloc[:, :-4].values)
label_1 = train_set['label_1']
label_2 = train_set['label_2']
label_3 = train_set['label_3']
label_4 = train_set['label_4']

X_valid = pd.DataFrame(valid_set.iloc[:, :-4].values)
label_1_valid = valid_set['label_1']
label_2_valid = valid_set['label_2']
label_3_valid = valid_set['label_3']
label_4_valid = valid_set['label_4']

#Initial accuracy is being checked after training through a svc model.
classifier.fit(X,label_3)
predicted_label3 = classifier.predict(X_valid)

print("accuracy_score: ",metrics.accuracy_score(label_3_valid, predicted_label3))
# print("f1_score: ",f1_score(label_1_valid, predicted_label1, average='weighted')) #f-1 score
# print("precision_score: ",metrics.precision_score(label_1_valid, predicted_label1, average='weighted' ))
# print("recall_score: ",metrics.recall_score(label_1_valid, predicted_label1, average='weighted'))

"""#Label 3"""

# @title PCA for Label 3
from sklearn.decomposition import PCA

X_test = pd.DataFrame(test_set.iloc[:, 1:].values)
#Validation
pca = PCA(n_components=0.95, svd_solver='full')
pca.fit(X)
x_train_pca = pd.DataFrame(pca.transform(X)) #train
x_valid_pca = pd.DataFrame(pca.transform(X_valid)) #valid
x_test_pca = pd.DataFrame(pca.transform(X_test))
print('Shape after PCA: ',x_train_pca.shape)

# @title svm classifier with pca
from sklearn import svm

# For classification with a linear kernel
classifier = svm.SVC(kernel='linear', C=1)

# For regression with a linear kernel
# classifier = svm.SVR(kernel='linear', C=1.0)

# Train the model
# classifier.fit(x_train_df, y_train_df)
classifier.fit(x_train_pca, label_3)

#predict for validation
y_valid_pred = classifier.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_3_valid, y_valid_pred))

# @title CatBoost with cpa
import catboost
from catboost import CatBoostClassifier, CatBoostRegressor

# For classification
classifier_cat_l3 = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)

# For regression
# classifier = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)

# Train the model
classifier_cat_l3.fit(x_train_pca, label_3, eval_set=(x_train_pca, label_3), verbose=100)

#predict for validation
y_valid_pred_l3_cat = classifier_cat_l3.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_3_valid, y_valid_pred_l3_cat))

#predict
#y_test_pred = classifier_cat_l2.predict(x_test_df)

# @title Catboost without cpa
# For classification
classifier_cat_l3 = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)

# For regression
# classifier = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)

# Train the model
classifier_cat_l3.fit(X, label_3, eval_set=(X, label_3), verbose=100)

#predict for validation
y_valid_pred_l3_cat = classifier_cat_l3.predict(X_valid)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_3_valid, y_valid_pred_l3_cat))

#predict
#y_test_pred = classifier_cat_l2.predict(x_test_df)

# @title making csv for label 3
predicted_label3_test = classifier.predict(x_test_pca)

predicted_df = pd.DataFrame({'label_3': predicted_label3_test})

# Save the DataFrame to a CSV file
predicted_df.to_csv('/content/drive/MyDrive/ML/Results/Label 12/predicted_L12_label3.csv', index=False)

# @title hyper parameter tuning for label 3
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, StratifiedKFold
from scipy.stats import uniform
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV,HalvingGridSearchCV

# Define the hyperparameter grid
param_grid = {
    'C': [0.1,1,10,20,100],
    'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],  # Experiment with different kernels
    'gamma':['scale', 'auto'],
    'degree': [1,2,3,4]

}

# Create an SVM classifier
svm_classifier_label3 = SVC(class_weight='balanced')

# Perform grid search with cross-validation
grid_search_label3 = HalvingGridSearchCV(svm_classifier_label3, param_grid, scoring='accuracy', cv=5,n_jobs=-1, factor=2, verbose=1)
grid_search_label3.fit(x_train_pca, label_3)

# Get the best model and hyperparameters
best_svm_classifier = grid_search_label3.best_estimator_
best_params_label3 = grid_search_label3.best_params_

# Make predictions on the validation set
y_pred_lable3 = best_svm_classifier.predict(x_valid_pca)

# Evaluate the model
print("Best Hyperparameters:", best_params_label3)
print("accuracy_score: ",metrics.accuracy_score(label_3_valid, y_pred_lable3))

# @title svm Classifier without pca
from sklearn import svm

# For classification with a linear kernel
classifier_label3 = svm.SVC(kernel='rbf', C=10, gamma='scale', degree=3)

# For regression with a linear kernel
# classifier = svm.SVR(kernel='linear', C=1.0)

# Train the model
# classifier.fit(x_train_df, y_train_df)
classifier_label3.fit(X, label_3)

#predict for validation
y_valid_pred = classifier_label3.predict(X_valid)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_3_valid, y_valid_pred))



# @title Random Forrest

from sklearn.ensemble import RandomForestClassifier  # For classification
# or
from sklearn.ensemble import RandomForestRegressor
# For classification

classifier_random = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
classifier_random.fit(X, label_3)

#predict for validation
y_valid_pred = classifier_random.predict(X_valid)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_3_valid, y_valid_pred))

#predict
#y_test_pred = classifier.predict(x_test_df)

"""#Label 4

"""

# @title svm classifier without pca
classifier_normal_l4 = SVC()

classifier_normal_l4.fit(X,label_4)
predicted_label4 = classifier_normal_l4.predict(X_valid)

print("accuracy_score: ",metrics.accuracy_score(label_4_valid, predicted_label4))
# print("f1_score: ",f1_score(label_1_valid, predicted_label1, average='weighted')) #f-1 score
# print("precision_score: ",metrics.precision_score(label_1_valid, predicted_label1, average='weighted' ))
# print("recall_score: ",metrics.recall_score(label_1_valid, predicted_label1, average='weighted'))

# @title CatBoost with pca
import catboost
from catboost import CatBoostClassifier, CatBoostRegressor

# For classification
classifier_cat_l4 = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)

# For regression
# classifier = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)

# Train the model
classifier_cat_l4.fit(x_train_pca, label_4, eval_set=(x_train_pca, label_4), verbose=100)

#predict for validation
y_valid_pred_l4_cat = classifier_cat_l4.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_4_valid, y_valid_pred_l4_cat))

#predict
#y_test_pred = classifier_cat_l2.predict(x_test_df)

# @title CatBoost without pca
import catboost
from catboost import CatBoostClassifier, CatBoostRegressor

# For classification
classifier_cat_l4_norm = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)

# For regression
# classifier = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)

# Train the model
classifier_cat_l4_norm.fit(X, label_4, eval_set=(X, label_4), verbose=100)

#predict for validation
y_valid_pred_l4_cat_norm = classifier_cat_l4_norm.predict(X_valid)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_4_valid, y_valid_pred_l4_cat_norm))

#predict
#y_test_pred = classifier_cat_l2.predict(x_test_df)

# @title Random Forrest without pca

from sklearn.ensemble import RandomForestClassifier  # For classification
# or
from sklearn.ensemble import RandomForestRegressor
# For classification

classifier_random_l4 = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
classifier_random_l4.fit(X, label_4)

#predict for validation
y_valid_pred_l4 = classifier_random_l4.predict(X_valid)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_4_valid, y_valid_pred_l4))

#predict
#y_test_pred = classifier.predict(x_test_df)

# @title Random Forrest with pca

from sklearn.ensemble import RandomForestClassifier  # For classification
# or
from sklearn.ensemble import RandomForestRegressor
# For classification

classifier_random_l4_pca = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
classifier_random_l4_pca.fit(x_train_pca, label_4)

#predict for validation
y_valid_pred_l4_pca = classifier_random_l4_pca.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_4_valid, y_valid_pred_l4_pca))

#predict
#y_test_pred = classifier.predict(x_test_df)

#@title making csv for label 4
predicted_label4_test = classifier_random_l4_pca.predict(x_test_pca)


predicted_df_l4 = pd.DataFrame({'label_4': predicted_label4_test})

# Save the DataFrame to a CSV file
predicted_df_l4.to_csv('/content/drive/MyDrive/ML/Results/Label 12/predicted_L12_label4.csv', index=False)

# @title svm classifier using PCA
from sklearn import svm

# For classification with a linear kernel
classifier_l4 = svm.SVC()

# For regression with a linear kernel
# classifier = svm.SVR(kernel='linear', C=1.0)

# Train the model
# classifier.fit(x_train_df, y_train_df)
classifier_l4.fit(x_train_pca, label_4)

#predict for validation
y_valid_pred_l4_pca = classifier_l4.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_4_valid, y_valid_pred_l4_pca))

#@title Hyper parameter tuning
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, StratifiedKFold
from scipy.stats import uniform
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV,HalvingGridSearchCV

# Define the hyperparameter grid
param_grid = {
    'C': [0.1,1,10,20,100],
    'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],  # Experiment with different kernels
    'gamma':['scale', 'auto'],
    'degree': [1,2,3,4]

}

# Create an SVM classifier
svm_classifier_label4 = SVC(class_weight='balanced')

# Perform grid search with cross-validation
grid_search_label4 = HalvingGridSearchCV(svm_classifier_label4, param_grid, scoring='accuracy', cv=5,n_jobs=-1, factor=2, verbose=1)
grid_search_label4.fit(x_train_pca, label_4)

# Get the best model and hyperparameters
best_svm_classifier_l4 = grid_search_label4.best_estimator_
best_params_label4 = grid_search_label4.best_params_

# Make predictions on the validation set
y_pred_lable4 = best_svm_classifier_l4.predict(x_valid_pca)

# Evaluate the model
print("Best Hyperparameters:", best_params_label4)
print("accuracy_score: ",metrics.accuracy_score(label_4_valid, y_pred_lable4))

"""#Label 2"""

#@title svm Classifier without pca
classifier_normal_l2 = SVC()

classifier_normal_l2.fit(X,label_2)
predicted_label2 = classifier_normal_l2.predict(X_valid)

print("accuracy_score: ",metrics.accuracy_score(label_2_valid, predicted_label2))
# print("f1_score: ",f1_score(label_1_valid, predicted_label1, average='weighted')) #f-1 score
# print("precision_score: ",metrics.precision_score(label_1_valid, predicted_label1, average='weighted' ))
# print("recall_score: ",metrics.recall_score(label_1_valid, predicted_label1, average='weighted'))

# @title Random Forrest without pca

from sklearn.ensemble import RandomForestClassifier  # For classification
# or
from sklearn.ensemble import RandomForestRegressor
# For classification

classifier_random_l2 = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
classifier_random_l2.fit(X, label_2)

#predict for validation
y_valid_pred_l2 = classifier_random_l2.predict(X_valid)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_2_valid, y_valid_pred_l2))

#predict
#y_test_pred = classifier.predict(x_test_df)

# @title Random Forrest with pca

from sklearn.ensemble import RandomForestClassifier  # For classification
# or
from sklearn.ensemble import RandomForestRegressor
# For classification

classifier_random_l2_pca = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
classifier_random_l2_pca.fit(x_train_pca, label_2)

#predict for validation
y_valid_pred_l2_pca = classifier_random_l2_pca.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_2_valid, y_valid_pred_l2_pca))

#predict
#y_test_pred = classifier.predict(x_test_df)

# @title svm classifier with PCA
from sklearn import svm

# For classification with a linear kernel
classifier_l2 = svm.SVC()

# For regression with a linear kernel
# classifier = svm.SVR(kernel='linear', C=1.0)

# Train the model
# classifier.fit(x_train_df, y_train_df)
classifier_l2.fit(x_train_pca, label_2)

#predict for validation
y_valid_pred_l2_pca = classifier_l2.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_2_valid, y_valid_pred_l2_pca))

!pip install catboost

# @title CatBoost with pca
import catboost
from catboost import CatBoostClassifier, CatBoostRegressor

# For classification
classifier_cat_l2 = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)

# For regression
# classifier = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)

# Train the model
classifier_cat_l2.fit(x_train_pca, label_2, eval_set=(x_train_pca, label_2), verbose=100)

#predict for validation
y_valid_pred_l2_cat = classifier_cat_l2.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_2_valid, y_valid_pred_l2_cat))

#predict
#y_test_pred = classifier_cat_l2.predict(x_test_df)

# @title CatBoost without pca
import catboost
from catboost import CatBoostClassifier, CatBoostRegressor

# For classification
classifier_cat_l2_norm = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)

# For regression
# classifier = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)

# Train the model
classifier_cat_l2_norm.fit(X, label_2, eval_set=(X, label_2), verbose=100)

#predict for validation
y_valid_pred_l2_cat_norm = classifier_cat_l2_norm.predict(X_valid)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_2_valid, y_valid_pred_l2_cat_norm))

#predict
#y_test_pred = classifier_cat_l2.predict(x_test_df)

#@title making csv for label 2
predicted_label2_test = classifier_cat_l2.predict(x_test_pca)
predicted_label2_test = predicted_label2_test.flatten()
predicted_label2_test = [int(value) for value in predicted_label2_test]

predicted_df_l2 = pd.DataFrame({'label_2': predicted_label2_test})

# Save the DataFrame to a CSV file
predicted_df_l2.to_csv('/content/drive/MyDrive/ML/Results/Label 12/predicted_L12_label2.csv', index=False)

#@title svm classifier with best parameters
classifier_normal_l2 = svm.SVC(kernel='rbf', C=100, gamma=0.001)

classifier_normal_l2.fit(X,label_2)
predicted_label2 = classifier_normal_l2.predict(X_valid)

print("accuracy_score: ",metrics.accuracy_score(label_2_valid, predicted_label2))
# print("f1_score: ",f1_score(label_1_valid, predicted_label1, average='weighted')) #f-1 score
# print("precision_score: ",metrics.precision_score(label_1_valid, predicted_label1, average='weighted' ))
# print("recall_score: ",metrics.recall_score(label_1_valid, predicted_label1, average='weighted'))

#@title svm classifier with best parameters
classifier_normal_l2norm = svm.SVC(kernel='rbf', C=100, gamma=0.001)

classifier_normal_l2norm.fit(X,label_2)
predicted_label2 = classifier_normal_l2norm.predict(X_valid)

print("accuracy_score: ",metrics.accuracy_score(label_2_valid, predicted_label2))
# print("f1_score: ",f1_score(label_1_valid, predicted_label1, average='weighted')) #f-1 score
# print("precision_score: ",metrics.precision_score(label_1_valid, predicted_label1, average='weighted' ))
# print("recall_score: ",metrics.recall_score(label_1_valid, predicted_label1, average='weighted'))

#@title making csv for label 2
predicted_label2_test = classifier_normal_l2norm.predict(X_test)
predicted_label2_test
# predicted_label2_test = predicted_label2_test.flatten()
# predicted_label2_test = [int(value) for value in predicted_label2_test]

# predicted_df_l2 = pd.DataFrame({'label_2': predicted_label2_test})

# # Save the DataFrame to a CSV file
# predicted_df_l2.to_csv('/content/drive/MyDrive/ML/Results/Label 12/test/predicted_L12_label2.csv', index=False)

predicted_label2_test = [int(value) for value in predicted_label2_test]
predicted_df_l2 = pd.DataFrame({'label_2': predicted_label2_test})

# # Save the DataFrame to a CSV file
predicted_df_l2.to_csv('/content/drive/MyDrive/ML/Results/Label 12/test/predicted_L12_label2final2.csv', index=False)

"""# Label 1"""

# @title CatBoost with pca
import catboost
from catboost import CatBoostClassifier, CatBoostRegressor

# For classification
classifier_cat_l1 = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6)

# For regression
# classifier = CatBoostRegressor(iterations=500, learning_rate=0.1, depth=6)

# Train the model
classifier_cat_l1.fit(x_train_pca, label_1, eval_set=(x_train_pca, label_1), verbose=100)

#predict for validation
y_valid_pred_l1_cat = classifier_cat_l1.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_1_valid, y_valid_pred_l1_cat))

#predict
#y_test_pred = classifier_cat_l2.predict(x_test_df)

# @title Random Forrest with pca

from sklearn.ensemble import RandomForestClassifier  # For classification
# or
from sklearn.ensemble import RandomForestRegressor
# For classification

classifier_random_l1_pca = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
classifier_random_l1_pca.fit(x_train_pca, label_1)

#predict for validation
y_valid_pred_l1_pca = classifier_random_l1_pca.predict(x_valid_pca)

#accuracy
print("accuracy_score: ",metrics.accuracy_score(label_1_valid, y_valid_pred_l1_pca))

#predict
#y_test_pred = classifier.predict(x_test_df)

#@title making csv for label 1
predicted_label1_test = classifier_random_l1_pca.predict(x_test_pca)


predicted_df_l1 = pd.DataFrame({'label_1': predicted_label1_test})

# Save the DataFrame to a CSV file
predicted_df_l1.to_csv('/content/drive/MyDrive/ML/Results/Label 12/predicted_L12_label1.csv', index=False)

#@title hyper parameter tuning
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, StratifiedKFold
from scipy.stats import uniform
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV,HalvingGridSearchCV

# Define the hyperparameter grid
param_grid = {
    'C': [0.1,1,10,20,100],
    'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],  # Experiment with different kernels
    'gamma':['scale', 'auto'],
    'degree': [1,2,3,4]

}

# Create an SVM classifier
svm_classifier_label1 = SVC(class_weight='balanced')

# Perform grid search with cross-validation
grid_search_label1 = HalvingGridSearchCV(svm_classifier_label1, param_grid, scoring='accuracy', cv=5,n_jobs=-1, factor=2, verbose=1)
grid_search_label1.fit(x_train_pca, label_1)

# Get the best model and hyperparameters
best_svm_classifier_l1 = grid_search_label1.best_estimator_
best_params_label1 = grid_search_label1.best_params_

# Make predictions on the validation set
y_pred_lable1 = best_svm_classifier_l1.predict(x_valid_pca)

# Evaluate the model
print("Best Hyperparameters:", best_params_label1)
print("accuracy_score: ",metrics.accuracy_score(label_1_valid, y_pred_lable1))

#@title svm classifier with best parameters
classifier_normal_l1 = svm.SVC(kernel='rbf', C=100, gamma=0.001)

classifier_normal_l1.fit(X,label_1)
predicted_label1 = classifier_normal_l1.predict(X_valid)

print("accuracy_score: ",metrics.accuracy_score(label_1_valid, predicted_label1))
# print("f1_score: ",f1_score(label_1_valid, predicted_label1, average='weighted')) #f-1 score
# print("precision_score: ",metrics.precision_score(label_1_valid, predicted_label1, average='weighted' ))
# print("recall_score: ",metrics.recall_score(label_1_valid, predicted_label1, average='weighted'))

predicted_label1_test = classifier_normal_l1.predict(X_test)


predicted_df_l1 = pd.DataFrame({'label_1': predicted_label1_test})

# Save the DataFrame to a CSV file
predicted_df_l1.to_csv('/content/drive/MyDrive/ML/Results/Label 12/test/predicted_L12_label1.csv', index=False)