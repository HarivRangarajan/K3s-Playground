import time
import pickle
import numpy as np
import logging
from kubernetes import client, config
from prometheus_api_client import PrometheusConnect
from collections import deque
from model import RequestPredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('scaling_agent')

class ScalingAgent:
    def __init__(self):
        self.predictor = RequestPredictor()
        with open('/app/model/linear_model.pkl', 'rb') as f:
            self.predictor.model = pickle.load(f)
            
        self.request_history = deque(maxlen=10)
        config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()
        self.prom = PrometheusConnect(url="http://prometheus-server.monitoring:9090", disable_ssl=True)
    
    def get_current_metrics(self):
        # Query last 5 minutes average request rate
        query = 'avg_over_time(sum(rate(ImdbAppDuration_count[1m]))[5m:])'
        result = self.prom.custom_query(query)
        if result:
            return float(result[0]['value'][1])
        return 0
    
    def scale_deployment(self, namespace, deployment, replicas):
        try:
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
    
    def run(self):
        while True:
            try:
                current_requests = self.get_current_metrics()
                logger.info(f"Current request rate: {current_requests}")
                
                self.request_history.append(current_requests)
                
                if len(self.request_history) == 10:
                    request_history_array = np.array(self.request_history)
                    logger.info(f"Input to model: {request_history_array}")
                    
                    needed_replicas = self.predictor.predict(request_history_array)
                    logger.info(f"Model prediction: {needed_replicas} replicas needed")
                    
                    self.scale_deployment("imdb", "imdb", needed_replicas)
                
                # Wait for 5 minutes before next check
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")
                time.sleep(300)

if __name__ == "__main__":
    agent = ScalingAgent()
    agent.run() 