import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('customer_churn_features.csv')

print("="*80)
print("CHURN PREDICTION - XGBOOST")
print("="*80)

print(f"\n✓ Data loaded: {len(df)} customers")
print(f"✓ Features: {df.shape[1]}")
print(f"\nChurn Distribution:")
print(df['churn'].value_counts())
print(f"Churn Rate: {df['churn'].mean()*100:.1f}%\n")

X = df[['frequency', 'monetary_value', 'avg_review_score', 
         'avg_payment_value', 'avg_installments', 'avg_delivery_delay']]
y = df['churn']

X = X.fillna(X.mean())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()

model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    n_jobs=-1,
    eval_metric='logloss'
)
model.fit(X_train_scaled, y_train)

train_acc = model.score(X_train_scaled, y_train)
test_acc = model.score(X_test_scaled, y_test)

print(f"✓ Model trained")
print(f"  Train Accuracy: {train_acc:.4f}")
print(f"  Test Accuracy: {test_acc:.4f}\n")

y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=['No Churn', 'Churn']))

roc_score = roc_auc_score(y_test, y_pred_proba)
print(f"ROC-AUC Score: {roc_score:.4f}\n")

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("Feature Importance:")
print(feature_importance.to_string(index=False))

df['churn_probability'] = model.predict_proba(scaler.transform(X))[:, 1]
df['churn_risk'] = pd.cut(df['churn_probability'], 
                           bins=[0, 0.33, 0.67, 1.0], 
                           labels=['Low', 'Medium', 'High'])

print(f"\n✓ Risk Segments:")
print(df['churn_risk'].value_counts())

output = df[['customer_id', 'recency_days', 'frequency', 'monetary_value', 
             'avg_review_score', 'churn_probability', 'churn_risk']]
output.to_csv('customer_churn_predictions.csv', index=False)

print(f"\n✓ Predictions saved to customer_churn_predictions.csv")
print("="*80)