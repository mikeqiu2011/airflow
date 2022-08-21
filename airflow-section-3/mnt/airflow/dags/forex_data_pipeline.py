from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor

default_args = {
    'owner': 'airflow',
    'email_on_failure': False,
    'email_on_retry': False,
    'email': 'admin@localhost.com',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# id unique across all DAG,
with DAG('forex_data_pipeline', start_date=datetime(2022, 8, 21),           schedule_interval='@daily', default_args=default_args, catchup=False) as dag:
    # is_forex_rates_available = HttpSensor(
    #     task_id='is_forex_rates_available',
    #     http_conn_id='forex_api',
    #     # endpoint='marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b',
    #     endpoint='todos/1',
    #     response_check=lambda resp: 'title' in resp.json(),
    #     poke_interval=5,
    #     timeout=20
    # )

    is_forex_file_available = FileSensor(
        task_id='is_forex_file_available',
        fs_conn_id='forex_path',
        filepath='forex_currencies.csv',
        poke_interval=5,
        timeout=20
    )
