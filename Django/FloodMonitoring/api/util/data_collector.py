
from api.util.helpers.blynk_listener import fetch_blynk_data
from api.util.helpers.ingester import ingest_datapoints
from api.util.helpers.model_predictor.predictor import predict_batch

from ..supabase.utils import push_blynk_data_to_supabase
import time

    
def run_data_collection_cycle():

    batch = fetch_blynk_data()

    if batch:
        new_data_batch = ingest_datapoints(batch)

        if new_data_batch:
            forecast_data_batch = predict_batch(new_data_batch)
            push_blynk_data_to_supabase(forecast_data_batch, new_data_batch)
    else:
        time.sleep(0.05)