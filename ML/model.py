import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

class RequestPredictor:
    def __init__(self):
        self.seq_length = 10
        # Load the trained model using joblib
        self.model = joblib.load('/app/model/linear_model.pkl')

    def predict(self, recent_requests):
        """
        Predict next minute's request count based on last 10 minutes
        Args:
            recent_requests: numpy array of last 10 minutes of request counts
        Returns:
            predicted_replicas: predicted number of replicas needed
        """
        if len(recent_requests) != self.seq_length:
            raise ValueError(f"Input must contain exactly {self.seq_length} values")

        # Convert to float type as per training data
        recent_requests = recent_requests.astype(float)

        # Reshape for model input (1, seq_length)
        X = recent_requests.reshape(1, -1)

        # Get prediction
        predicted_requests = self.model.predict(X)[0]

        # Convert predicted requests to number of replicas needed
        # Assuming each replica can handle 100 requests per minute
        needed_replicas = max(1, int(np.ceil(predicted_requests / 100)))

        # # Assuming each replica can handle 50 requests per minute
        # needed_replicas = max(1, int(np.ceil(predicted_requests / 50)))

        return needed_replicas
