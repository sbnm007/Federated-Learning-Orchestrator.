#!/usr/bin/env python3
"""
Federated Learning Client
Runs on individual client machines to participate in federated learning
"""

import socket
import json
import numpy as np
import pickle
import time
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class FederatedClient:
    def __init__(self, client_id, server_host='localhost', server_port=8080):
        self.client_id = client_id
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.weights = None
        self.local_accuracy = 0.0
        self.round_number = 0
        self.running = False
        
    def setup_data(self, n_samples=300, n_features=10):
        """Generate local training data"""
        print(f"📊 Setting up data for {self.client_id}...")
        
        # Generate different data distributions for different clients
        # This simulates different organizations having different data
        random_state = hash(self.client_id) % 1000
        
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=8,
            n_redundant=2,
            n_clusters_per_class=1,
            random_state=random_state
        )
        
        # Split into train/test
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Initialize model
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        
        print(f"✅ Data setup completed for {self.client_id}:")
        print(f"   Training samples: {len(self.X_train)}")
        print(f"   Test samples: {len(self.X_test)}")
        print(f"   Features: {self.X_train.shape[1]}")
        
    def connect_to_server(self):
        """Connect to the aggregator server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            print(f"🔗 Connected to aggregator server at {self.server_host}:{self.server_port}")
            
            # Register with server
            self.register_with_server()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False
    
    def register_with_server(self):
        """Register this client with the aggregator server"""
        message = {
            'type': 'register',
            'client_id': self.client_id,
            'info': {
                'n_samples': len(self.X_train),
                'n_features': self.X_train.shape[1]
            }
        }
        
        self.send_message(message)
        print(f"📝 Registered with server as {self.client_id}")
    
    def start_client(self):
        """Start the client and listen for server messages"""
        self.running = True
        
        try:
            while self.running:
                message = self.receive_message()
                if not message:
                    break
                
                if message['type'] == 'registered':
                    print(f"✅ Registration confirmed by server")
                    
                elif message['type'] == 'start_training':
                    self.round_number = message['round']
                    print(f"\n🎯 Starting training round {self.round_number}")
                    self.train_local_model()
                    
                elif message['type'] == 'global_weights':
                    self.receive_global_weights(message)
                    
                elif message['type'] == 'pong':
                    print("🏓 Received pong from server")
                    
        except Exception as e:
            print(f"❌ Client error: {e}")
        finally:
            self.cleanup()
    
    def train_local_model(self):
        """Train the local model on client data"""
        print(f"🤖 Training local model for {self.client_id}...")
        
        # Train model
        self.model.fit(self.X_train, self.y_train)
        
        # Evaluate local model
        y_pred = self.model.predict(self.X_test)
        self.local_accuracy = accuracy_score(self.y_test, y_pred)
        
        # Extract weights
        self.weights = np.concatenate([
            self.model.coef_.flatten(),
            self.model.intercept_
        ])
        
        print(f"✅ Local training completed:")
        print(f"   Local accuracy: {self.local_accuracy:.4f}")
        print(f"   Weights shape: {self.weights.shape}")
        
        # Send weights to server
        self.send_weights_to_server()
    
    def send_weights_to_server(self):
        """Send local weights to the aggregator server"""
        try:
            weights_hex = pickle.dumps(self.weights).hex()
            
            message = {
                'type': 'weights',
                'client_id': self.client_id,
                'weights': weights_hex,
                'accuracy': self.local_accuracy,
                'samples': len(self.X_train),
                'round': self.round_number
            }
            
            self.send_message(message)
            print(f"📤 Sent weights to server")
            
        except Exception as e:
            print(f"❌ Failed to send weights: {e}")
    
    def receive_global_weights(self, message):
        """Receive and apply global weights from server"""
        try:
            weights_hex = message['weights']
            global_weights = pickle.loads(bytes.fromhex(weights_hex))
            
            # Apply global weights to local model
            n_features = self.X_train.shape[1]
            self.model.coef_ = global_weights[:n_features].reshape(1, -1)
            self.model.intercept_ = global_weights[n_features:]
            
            # Evaluate with global weights
            y_pred = self.model.predict(self.X_test)
            global_accuracy = accuracy_score(self.y_test, y_pred)
            
            print(f"📥 Received global weights:")
            print(f"   Global accuracy: {global_accuracy:.4f}")
            print(f"   Local accuracy:  {self.local_accuracy:.4f}")
            print(f"   Improvement:     {global_accuracy - self.local_accuracy:.4f}")
            
            # Update local weights
            self.weights = global_weights
            
        except Exception as e:
            print(f"❌ Error receiving global weights: {e}")
    
    def send_message(self, message):
        """Send a JSON message to the server"""
        try:
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            message_length = len(message_bytes)
            
            # Send message length first (4 bytes)
            self.socket.send(message_length.to_bytes(4, byteorder='big'))
            # Send actual message
            self.socket.send(message_bytes)
            
        except Exception as e:
            raise Exception(f"Failed to send message: {e}")
    
    def receive_message(self):
        """Receive a JSON message from the server"""
        try:
            # Receive message length first (4 bytes)
            length_bytes = self.socket.recv(4)
            if len(length_bytes) != 4:
                return None
                
            message_length = int.from_bytes(length_bytes, byteorder='big')
            
            # Receive actual message
            message_bytes = b''
            while len(message_bytes) < message_length:
                chunk = self.socket.recv(min(4096, message_length - len(message_bytes)))
                if not chunk:
                    return None
                message_bytes += chunk
            
            message_json = message_bytes.decode('utf-8')
            return json.loads(message_json)
            
        except Exception as e:
            print(f"❌ Error receiving message: {e}")
            return None
    
    def cleanup(self):
        """Clean up client resources"""
        print(f"\n🧹 Cleaning up client {self.client_id}...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("✅ Client cleanup completed")

def main():
    """Main function to run a federated learning client"""
    print("🎉 FEDERATED LEARNING CLIENT")
    print("=" * 50)
    
    # Configuration
    CLIENT_ID = input("Enter client ID (e.g., client_1): ").strip() or f"client_{int(time.time())}"
    SERVER_HOST = input("Enter server host (default: localhost): ").strip() or "localhost"
    SERVER_PORT = input("Enter server port (default: 8080): ").strip() or "8080"
    
    try:
        SERVER_PORT = int(SERVER_PORT)
    except ValueError:
        print("❌ Invalid port number")
        return
    
    # Create client
    client = FederatedClient(CLIENT_ID, SERVER_HOST, SERVER_PORT)
    
    try:
        # Setup data
        client.setup_data()
        
        # Connect to server
        if client.connect_to_server():
            print(f"🚀 Starting federated learning client {CLIENT_ID}")
            print("   Waiting for server instructions...")
            
            # Start client loop
            client.start_client()
        else:
            print("❌ Failed to connect to server")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Client {CLIENT_ID} interrupted by user")
    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        client.cleanup()

if __name__ == "__main__":
    main()
