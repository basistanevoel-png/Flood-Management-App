from collections import deque

def engineer_features_for_sensor(reading_queue: deque) -> dict:
    wlvl_now = reading_queue[-1]
    wlvl_lag_1 = reading_queue[-2] if len(reading_queue) > 1 else 0.0
    wlvl_lag_2 = reading_queue[-3] if len(reading_queue) > 2 else 0.0
    wlvl_lag_5 = reading_queue[-6] if len(reading_queue) > 5 else 0.0
    wlvl_lag_10 = reading_queue[-11] if len(reading_queue) > 10 else 0.0

    diff_lag_1 = wlvl_now - wlvl_lag_1 if (wlvl_lag_1 is not None and wlvl_lag_1 != 0) else 0.0
    pct_change_lag_1 = (diff_lag_1 / wlvl_lag_1 * 100) if (wlvl_lag_1 is not None and wlvl_lag_1 != 0) else 0.0

    slope_lag_10 = 0.0
    if wlvl_lag_10 != 0.0:
        slope_lag_10 = (wlvl_now - wlvl_lag_10) / 10

    return {
        'wlvl_now': wlvl_now,
        'wlvl_lag_1': wlvl_lag_1,
        'wlvl_lag_2': wlvl_lag_2,
        'wlvl_lag_5': wlvl_lag_5,
        'wlvl_lag_10': wlvl_lag_10,
        'diff_lag_1': diff_lag_1,
        'pct_change_lag_1': pct_change_lag_1,
        'slope_lag_10': slope_lag_10,
    }

def engineer_features_for_weather_api(rainfall_history: deque) -> dict:

    values = [rain for (_, rain) in rainfall_history]

    return {
        "rainfall_hr1": values[-1] if len(values) >= 1 else 0.0,
        "rainfall_hr2": sum(values[-2:]) if len(values) >= 2 else 0.0,
        "rainfall_hr12": sum(values[-12:]) if len(values) >= 12 else sum(values),
        "rainfall_hr24": sum(values[-24:]) if len(values) >= 24 else sum(values),
    }
