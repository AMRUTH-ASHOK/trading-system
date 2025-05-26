import joblib
import pathlib
import pandas as pd

MODEL_PATH = pathlib.Path(__file__).resolve().parents[2] / "models" / "model.joblib"


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model file missing; train it first.")
    return joblib.load(MODEL_PATH)


def predict_proba(model, feat_df: pd.DataFrame):
    feat_cols = [c for c in feat_df.columns if c not in ("timestamp", "symbol")]
    X = feat_df[feat_cols]
    return model.predict_proba(X)[:, 1]  # assume binary classifier returns P(BUY)
