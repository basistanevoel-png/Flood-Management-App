import pandas as pd

from api.utils import find_category

from .model_loader import get_model

FEATURE_ORDER = [
    "rainfall_hr1",
    "rainfall_hr2",
    "rainfall_hr12",
    "rainfall_hr24",
    "wlvl_now",
    "wlvl_lag_1",
    "wlvl_lag_2",
    "wlvl_lag_5",
    "wlvl_lag_10",
    "diff_lag_1",
    "pct_change_lag_1",
    "slope_lag_10",
]


def predict_batch(datapoint_batch):
    if not datapoint_batch:
        return []

    model = get_model()

    df = pd.DataFrame(datapoint_batch)

    for col in FEATURE_ORDER:
        if col not in df.columns:
            df[col] = 0.0

    X = df.reindex(columns=FEATURE_ORDER)

    X = X.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    preds = model.predict(X)

    forecast_json = []

    for i, dp in enumerate(datapoint_batch):
        prediction = float(preds[i])

        forecast_json.append({
            "sensor_id": dp["sensor_id"],
            "timestamp": dp["timestamp"],
            "forecast": prediction,
            "forecast_category": find_category(prediction)
        })

    return forecast_json