from datetime import datetime, timedelta
import json
import requests
import csv
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'airflow',
    'email_on_failure': False,
    'email_on_retry': False,
    'email': 'admin@localhost.com',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Download forex rates according to the currencies we want to watch
# described in the file forex_currencies.csv


def download_rates():
    BASE_URL = "https://gist.githubusercontent.com/marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b/raw/"
    ENDPOINTS = {
        'USD': 'api_forex_exchange_usd.json',
        'EUR': 'api_forex_exchange_eur.json'
    }
    with open('/opt/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for idx, row in enumerate(reader):
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get(f"{BASE_URL}{ENDPOINTS[base]}").json()
            outdata = {'base': base, 'rates': {},
                       'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/opt/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')


# id unique across all DAG,
with DAG('forex_data_pipeline', start_date=datetime(2022, 8, 21),    schedule_interval='@daily', default_args=default_args, catchup=False) as dag:
    is_forex_rates_available = HttpSensor(
        task_id='is_forex_rates_available',
        http_conn_id='forex_api',
        # endpoint='marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b',
        endpoint='todos/1',
        response_check=lambda resp: 'title' in resp.json(),
        poke_interval=5,
        timeout=20
    )

    is_forex_file_available = FileSensor(
        task_id='is_forex_file_available',
        fs_conn_id='forex_path',
        filepath='forex_currencies.csv',
        poke_interval=5,
        timeout=20
    )

    is_download_successful = PythonOperator(
        task_id='is_download_successful',
        python_callable=download_rates,
    )

    saving_rates = BashOperator(
        task_id='saving_rates',
        bash_command="""
            hdfs dfs -mkdir -p /forex &&
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
        """
    )
