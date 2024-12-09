import time
import numpy as np
import logging
from kubernetes import client, config
from prometheus_api_client import PrometheusConnect
from collections import deque
from model import RequestPredictor
import matplotlib.pyplot as plt
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scaling_agent')

class ScalingAgent:
    def __init__(self):
        # Initialize request predictor
        self.predictor = RequestPredictor()

        # Initialize request history with 10 minute window
        self.request_history = deque(maxlen=10)

        # For plotting the replicas required over time
        self.timestamps = []
        self.replicas = []

        # Configure Kubernetes client
        config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()

        # Configure Prometheus client with internal cluster DNS
        self.prom = PrometheusConnect(
            url="http://prometheus-service.monitoring.svc.cluster.local:8080",
            disable_ssl=True
        )

        logger.info("Scaling agent initialized successfully")

    def get_current_metrics(self):
        """Get the request rate for the last minute"""
        try:
            # Query last minute's request rate
            query = 'sum(rate(ImdbAppDuration_count[1m]))'
            result = self.prom.custom_query(query)

            if result and result[0]['value']:
                request_rate = float(result[0]['value'][1])
                # Convert to requests per minute
                requests_per_minute = request_rate * 60
                logger.info(f"Current request rate: {requests_per_minute:.2f} requests/minute")
                return requests_per_minute

            logger.warning("No metrics received from Prometheus")
            return 0

        except Exception as e:
            logger.error(f"Error getting metrics from Prometheus: {e}")
            return 0

    def scale_deployment(self, namespace, deployment, replicas):
        """Scale the deployment to the specified number of replicas"""
        try:
            # Get current replica count
            current = self.apps_v1.read_namespaced_deployment(
                name=deployment,
                namespace=namespace
            )
            current_replicas = current.spec.replicas

            if current_replicas != replicas:
                self.apps_v1.patch_namespaced_deployment_scale(
                    name=deployment,
                    namespace=namespace,
                    body={"spec": {"replicas": replicas}}
                )
                logger.info(f"Scaled {deployment} from {current_replicas} to {replicas} replicas")
            else:
                logger.info(f"No scaling needed. Current replicas: {current_replicas}")

        except Exception as e:
            logger.error(f"Error scaling deployment: {e}")

    def plot_replicas(self):
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(self.timestamps, self.replicas, marker='o')
            plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
            plt.title('Needed Replicas Over Time')
            plt.xlabel('Time')
            plt.ylabel('Number of Replicas')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig('replicas_over_time.png')
            logger.info("Plot saved as replicas_over_time.png")
        except Exception as e:
            logger.error(f"Error in plotting replica: {e}")


    def run(self):
        """Main loop for the scaling agent"""
        logger.info("Starting scaling agent main loop")

        while True:
            try:
                # Get current metrics (requests per minute)
                current_requests = self.get_current_metrics()
                self.request_history.append(current_requests)

                # Wait until we have enough history
                if len(self.request_history) == 10:
                    # Convert to numpy array and ensure float type
                    request_history_array = np.array(list(self.request_history), dtype=float)
                    logger.info(f"Request history (last 10 minutes): {request_history_array}")

                    # Get prediction from model
                    needed_replicas = self.predictor.predict(request_history_array)
                    logger.info(f"Model prediction: {needed_replicas} replicas needed")

                    current_time = datetime.now()

                    self.timestamps.append(current_time)
                    self.replicas.append(needed_replicas)

                    # Scale the deployment
                    self.scale_deployment("imdb", "imdb", needed_replicas)
                else:
                    logger.info(f"Building history: {len(self.request_history)}/10 minutes")

                # ### Testing the pod scaling ###
                # needed_replicas = 7 ## test the scaling agent without the model predictions
                # logger.info(f"Test: {needed_replicas} replicas needed")
                # self.scale_deployment("imdb", "imdb", needed_replicas)

                # Wait for 1 minute before next check
                logger.info("Waiting 1 minute before next check")
                self.plot_replicas()
                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    try:
        agent = ScalingAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Fatal error in scaling agent: {e}")
        raise
