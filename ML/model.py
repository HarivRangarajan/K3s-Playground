import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

class RequestPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.seq_length = 10
        
    def create_sequences(self, data, seq_length):
        xs = []
        for i in range(len(data) - seq_length + 1):
            xs.append(data[i:i+seq_length])
        return np.array(xs)
    
    def predict(self, recent_requests):
        """
        Predict next minute's request count based on last 10 minutes
        Args:
            recent_requests: numpy array of last 10 minutes of request counts
        Returns:
            predicted_requests: predicted number of requests for next minute
        """
        if len(recent_requests) != self.seq_length:
            raise ValueError(f"Input must contain exactly {self.seq_length} values")
            
        X = self.create_sequences(recent_requests, self.seq_length)
        prediction = self.model.predict(X)
        return max(1, int(prediction[0]))  # Ensure at least 1 replica 