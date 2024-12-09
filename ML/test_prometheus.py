## Script that you can use to test prometheus queries, from the jumpbox pod ##

from prometheus_api_client import PrometheusConnect
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('prometheus_test')

def test_prometheus_connection():
    prom = PrometheusConnect(
        url="http://prometheus-service.monitoring.svc.cluster.local:8080",
        disable_ssl=True
    )

    try:
        query = 'sum(rate(ImdbAppDuration_count[1m]))'
        result = prom.custom_query(query)

        if result and result[0]['value']:
            request_rate = float(result[0]['value'][1])
            requests_per_minute = request_rate * 60
            logger.info(f"Current request rate: {requests_per_minute:.2f} requests/minute")
        else:
            logger.warning("No metrics received from Prometheus")

    except Exception as e:
        logger.error(f"Error getting metrics from Prometheus: {e}")

if __name__ == "__main__":
    while True:
        test_prometheus_connection()
        time.sleep(10)
