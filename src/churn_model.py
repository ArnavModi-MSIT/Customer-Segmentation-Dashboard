import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
import warnings

warnings.filterwarnings("ignore")

# NOTE: 'frequency' intentionally excluded — with ~97% of customers at
# frequency=1 (see churn_features.py), it's near-constant and would make
# the model appear to hinge on a single low-variance feature rather than
# genuine behavioral signal. 'recency_days' is excluded too since it
# directly defines the churn label (would be leakage).
FEATURE_COLUMNS = [
    "monetary_value",
    "avg_review_score",
    "avg_payment_value",
    "avg_installments",
    "avg_delivery_delay",
]


def prepare_features(df):
    X = df[FEATURE_COLUMNS].copy()
    X = X.fillna(X.mean())
    y = df["churn"]
    return X, y


def train_churn_model(df, verbose=True):
    X, y = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

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
        eval_metric="logloss",
    )
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

    metrics = {
        "train_accuracy": model.score(X_train_scaled, y_train),
        "test_accuracy": model.score(X_test_scaled, y_test),
        "roc_auc": roc_auc_score(y_test, y_pred_proba),
        "classification_report": classification_report(y_test, y_pred, target_names=["No Churn", "Churn"]),
    }

    feature_importance = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)

    if verbose:
        print("=" * 80)
        print("CHURN MODEL — XGBOOST")
        print("=" * 80)
        print(f"Train Accuracy: {metrics['train_accuracy']:.4f}")
        print(f"Test Accuracy:  {metrics['test_accuracy']:.4f}")
        print(f"ROC-AUC:        {metrics['roc_auc']:.4f}\n")
        print(metrics["classification_report"])
        print("Feature Importance:")
        print(feature_importance.to_string(index=False))
        print("=" * 80)

    return model, scaler, metrics, feature_importance


def score_all_customers(df, model, scaler):
    X = df[FEATURE_COLUMNS].copy()
    X = X.fillna(X.mean())
    X_scaled = scaler.transform(X)

    df = df.copy()
    df["churn_probability"] = model.predict_proba(X_scaled)[:, 1]
    df["churn_risk"] = pd.cut(
        df["churn_probability"], bins=[0, 0.33, 0.67, 1.0], labels=["Low", "Medium", "High"]
    )
    return df


def run_churn_model(features_df, verbose=True):
    model, scaler, metrics, feature_importance = train_churn_model(features_df, verbose=verbose)
    scored = score_all_customers(features_df, model, scaler)

    if verbose:
        print("\nRisk Segments:")
        print(scored["churn_risk"].value_counts())

    return scored[["customer_unique_id", "recency_days", "monetary_value", "avg_review_score",
                    "churn_probability", "churn_risk"]], metrics, feature_importance


if __name__ == "__main__":
    features_df = pd.read_csv("outputs/customer_churn_features.csv")
    predictions, metrics, feature_importance = run_churn_model(features_df)
    predictions.to_csv("outputs/customer_churn_predictions.csv", index=False)
    print("\n✓ Exported to outputs/customer_churn_predictions.csv")
