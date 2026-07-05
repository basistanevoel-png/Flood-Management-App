from datetime import datetime, timedelta, timezone
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from .client import supabase

def push_blynk_data_to_supabase(forecast_data_batch, new_data_batch):

    sensor_map = {
        (row['sensor_id'], row['timestamp']): row
        for row in new_data_batch
    }

    for prediction_row in forecast_data_batch:

        key = (prediction_row['sensor_id'], prediction_row['timestamp'])
        sensor_row = sensor_map.get(key)

        if not sensor_row:
            print(f"[SUPABASE] WARNING: Missing sensor row for {key}")
            continue

        row_id = _log_sensor_and_api_data(sensor_row)
        _log_ml_prediction(prediction_row, row_id)

def _log_sensor_and_api_data(row_data):
    try:
        table = supabase.table('SENSOR_AND_API_DATA')
        data = {
            "sensor_id": row_data['sensor_id'],
            "timestamp": row_data['timestamp'],
            "wlvl_now": row_data['wlvl_now'],
            "wlvl_lag_t-1": row_data['wlvl_lag_1'],
            "wlvl_lag_t-2": row_data['wlvl_lag_2'],
            "wlvl_lag_t-5": row_data['wlvl_lag_5'],
            "wlvl_lag_t-10": row_data['wlvl_lag_10'],
            "diff_lag_t-1": row_data['diff_lag_1'],
            "pct_change_lag_t-1": row_data['pct_change_lag_1'],
            "slope_lag_t-10": row_data['slope_lag_10'],
            "rainfall_hr1": row_data['rainfall_hr1'],
            "rainfall_hr2": row_data['rainfall_hr2'],
            "rainfall_hr12": row_data['rainfall_hr12'],
            "rainfall_hr24": row_data['rainfall_hr24'],
            "flood_cat_now": row_data['flood_cat_now'],
            "temperature": row_data['weather_info']['temperature'],
            "description": row_data['weather_info']['description'],
            "pressure": row_data['weather_info']['pressure'],
            "icon_code": row_data['weather_info']['iconCode']
        }
        response = table.insert(data).execute()

        inserted_row = response.data[0]['id']
        return inserted_row
    
    except Exception as e:
        print("SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

def _log_ml_prediction(row_data, foreign_id):

    try:
        table = supabase.table('PREDICTIONS')
        data = {
            "data_id": foreign_id,
            "forecast": row_data['forecast'],
            "forecast_category": row_data['forecast_category']
        }

        response = table.insert(data).execute()

        return response.data
    
    except Exception as e:
        print("SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

def get_latest_data_from_supabase():
    try:

        sensor_response = (
            supabase.table("SENSOR_AND_API_DATA") 
            .select("*") 
            .order("timestamp", desc=True) 
            .execute()
        )

        rows = sensor_response.data

        latest_per_sensor = {}

        for row in rows:
            sensor_id = row["sensor_id"]

            if sensor_id not in latest_per_sensor:
                latest_per_sensor[sensor_id] = row

        latest_rows = list(latest_per_sensor.values())

        prediction_response = supabase.table("PREDICTIONS") \
            .select("*") \
            .execute()

        predictions = prediction_response.data

        prediction_map = {
            p["data_id"]: p for p in predictions
        }

        result = []

        for row in latest_rows:
            sensor_id = row["sensor_id"]
            row_id = row["id"]

            result.append({
                **row,
                "prediction": prediction_map.get(row_id)
            })

        return result
    
    except Exception as e:
        print("SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")


def get_latest_data_from_supabase():
    try:

        sensor_response = (
            supabase.table("SENSOR_AND_API_DATA") 
            .select("*") 
            .order("timestamp", desc=True) 
            .execute()
        )

        rows = sensor_response.data

        latest_per_sensor = {}

        for row in rows:
            sensor_id = row["sensor_id"]

            if sensor_id not in latest_per_sensor:
                latest_per_sensor[sensor_id] = row

        latest_rows = list(latest_per_sensor.values())

        prediction_response = supabase.table("PREDICTIONS") \
            .select("*") \
            .execute()

        predictions = prediction_response.data

        prediction_map = {
            p["data_id"]: p for p in predictions
        }

        result = []

        for row in latest_rows:
            sensor_id = row["sensor_id"]
            row_id = row["id"]

            result.append({
                **row,
                "prediction": prediction_map.get(row_id)
            })

        return result
    
    except Exception as e:
        print("SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

def get_latest_sensor_wl_data_from_supabase(sensor_id):
    try:
        sensor_response = (
            supabase.table("SENSOR_AND_API_DATA")
            .select("id, sensor_id, timestamp, wlvl_now, flood_cat_now")
            .eq("sensor_id", sensor_id)
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )

        rows = sensor_response.data or []
        if not rows:
            return None

        row = rows[0]
        row_id = row.get("id")

        prediction_response = (
            supabase.table("PREDICTIONS")
            .select("forecast, forecast_category")
            .eq("data_id", row_id)
            .limit(1)
            .execute()
        )

        prediction = (prediction_response.data or [{}])[0] if prediction_response.data else {}

        return {
            **row,
            "prediction": prediction
        }

    except Exception as e:
        print("[SUPABASE ERROR]")
        print(type(e).__name__)
        print(str(e))
        return None

def get_sensor_history_from_supabase(sensor_id):

    try:

        now = datetime.now(timezone.utc)

        end_time = now.replace(
            minute=0,
            second=0,
            microsecond=0
        )

        start_time = end_time - timedelta(hours=23)

        response = (
            supabase.table("SENSOR_AND_API_DATA")
            .select("timestamp, wlvl_now")
            .eq("sensor_id", sensor_id)
            .gte("timestamp", start_time.isoformat())
            .lte("timestamp", end_time.isoformat())
            .execute()
        )

        rows = response.data or []

        hourly_totals = defaultdict(list)

        for entry in rows:

            ts = datetime.fromisoformat(
                entry["timestamp"].replace("Z", "+00:00")
            )

            hour_key = ts.strftime("%Y-%m-%d %H:00")

            hourly_totals[hour_key].append(
                float(entry.get("wlvl_now") or 0.0)
            )

        history_map = {
            key: sum(values) / len(values)
            for key, values in hourly_totals.items()
        }

        hourlyData = []
        labels = []

        for i in range(24):

            current_slot = start_time + timedelta(hours=i)

            slot_key = current_slot.strftime("%Y-%m-%d %H:00")

            labels.append(
                current_slot.strftime("%H:00")
            )

            wlvl = history_map.get(slot_key, 0.0)

            hourlyData.append({
                "x": float(i),
                "y": round(wlvl, 2)
            })

        return {
            "hourly_data": hourlyData,
            "labels": labels
        }

    except Exception as e:

        print("[SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

        return {
            "hourly_data": [],
            "labels": []
        }

def get_web_chart_data_from_supabase(sensor_id="all", time_range="hour"):

    try:

        now = datetime.now(timezone.utc)

        #time range for the past year
        if time_range == "year":

            start_time = (
                now - relativedelta(months=11)
            ).replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            slots = 12

        #time range for the past month
        elif time_range == "month":

            start_time = (
                now - timedelta(days=30)
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            slots = 31

        #time range for the past week
        elif time_range == "week":

            start_time = (
                now - timedelta(days=7)
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            slots = 8

        #time range for the past day
        elif time_range == "day":

            start_time = (
                now - timedelta(hours=23)
            ).replace(
                minute=0,
                second=0,
                microsecond=0
            )

            slots = 24

        #time range for the past hour
        else:

            base_now = now.replace(
                minute=(now.minute // 5) * 5,
                second=0,
                microsecond=0
            )

            start_time = base_now - timedelta(minutes=55)

            slots = 12

        query = (
            supabase.table("SENSOR_AND_API_DATA")
            .select("sensor_id, timestamp, wlvl_now")
            .gte("timestamp", start_time.isoformat())
            .lte("timestamp", now.isoformat())
        )

        if sensor_id != "all":
            query = query.eq("sensor_id", sensor_id)

        response = query.execute()

        raw_data = response.data or []

        sensor_query = (
            supabase.table("SENSORS")
            .select("sensor_id, location_name")
        )

        if sensor_id != "all":
            sensor_query = sensor_query.eq("sensor_id", sensor_id)

        sensors_response = sensor_query.execute()

        sensors = sensors_response.data or []

        history_totals = defaultdict(list)

        for entry in raw_data:

            ts = datetime.fromisoformat(
                entry["timestamp"].replace("Z", "+00:00")
            )

            s_id = entry["sensor_id"]

            # YEAR: split into MONTHLY buckets
            if time_range == "year":

                bucket_dt = ts.replace(
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                )

            # MONTH/WEEK: split into DAY buckets
            elif time_range in ["month", "week"]:

                bucket_dt = ts.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                )

            # DAY: split into HOURLY buckets
            elif time_range == "day":

                bucket_dt = ts.replace(
                    minute=0,
                    second=0,
                    microsecond=0
                )

            # HOUR: split into 5-MINUTE buckets (this is because the temporal interval between sensor readings are 5 minutes)
            else:

                minute_bucket = (ts.minute // 5) * 5

                bucket_dt = ts.replace(
                    minute=minute_bucket,
                    second=0,
                    microsecond=0
                )

            key = (s_id, bucket_dt.isoformat())

            history_totals[key].append(
                float(entry.get("wlvl_now") or 0.0)
            )

        history_map = {
            key: sum(values) / len(values)
            for key, values in history_totals.items()
        }

        datasets = []

        for sensor in sensors:

            points = []

            for i in range(slots):

                if time_range == "year":

                    current_slot = (
                        start_time + relativedelta(months=i)
                    )

                elif time_range in ["month", "week"]:

                    current_slot = (
                        start_time + timedelta(days=i)
                    )

                elif time_range == "day":

                    current_slot = (
                        start_time + timedelta(hours=i)
                    )

                else:

                    current_slot = (
                        start_time + timedelta(minutes=i * 5)
                    )

                slot_key = current_slot.isoformat()

                wlvl = history_map.get(
                    (sensor["sensor_id"], slot_key),
                    0.0
                )

                points.append({
                    "x": slot_key,
                    "y": round(wlvl, 2)
                })

            datasets.append({
                "label": f"{sensor['sensor_id']} ({sensor['location_name']})",
                "data": points
            })

        return {
            "datasets": datasets
        }

    except Exception as e:

        print("[SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

        return {
            "datasets": []
        }

def get_vehicle_thresholds_from_supabase():

    try:
        response = (
            supabase.table("THRESHOLDS")
            .select("*")
            .execute()
        )

        print('[SUPABASE] query success for: vehicle threshold details')
        print (f'Rows fetched: {len(response.data)}')

        return response.data

    except Exception as e:
        print("SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

def get_sensor_details_from_supabase():
    try:
        response = (
            supabase.table("SENSORS")
            .select("*")
            .execute()
        )

        print('[SUPABASE] query success for: sensor details')
        print (f'Rows fetched: {len(response.data)}')

        return response.data

    except Exception as e:
        print("SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

def get_specific_sensor_details_from_supabase(sensor_id):

    try:

        response = (
            supabase.table("SENSORS")
            .select("*")
            .eq("sensor_id", sensor_id)
            .single()
            .execute()
        )

        sensor = response.data

        sensor["latlong"] = [
            sensor.pop("latitude"),
            sensor.pop("longitude")
        ]

        print(f"[SUPABASE] query success for: sensor {sensor_id} details")

        return sensor

    except Exception as e:

        print("[SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

        return None
    
def get_emergency_contacts_from_supabase():
    try:

        response = (
            supabase.table("EMERGENCY")
            .select("*")
            .execute()
        )

        print('[SUPABASE] query success for: emergency contact details')
        print (f'Rows fetched: {len(response.data)}')

        return response.data

    except Exception as e:
        print("[SUPABASE] ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")