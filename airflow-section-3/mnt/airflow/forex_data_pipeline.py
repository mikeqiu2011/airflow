from datetime import datetime, timedelta
from airflow import DAG

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
