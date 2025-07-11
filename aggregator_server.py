#!/usr/bin/env python3
"""
Federated Learning Aggregator Server
Runs on a central server to coordinate federated learning
"""

import socket
import threading
import json
import numpy as np
import pickle
import time
from datetime import datetime

class FederatedAggregator:
    def __init__(self, host='localhost', port=8080, target_clients=3):
        self.host = host
        self.port = port
        self.target_clients = target_clients
        self.clients = {}
        self.received_weights = []
        self.client_info = []
        self.round_number = 0
        self.global_weights = None
        self.server_socket = None
        self.running = False
        
    def start_server(self):
        """Start the aggregator server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🎯 Federated Aggregator Server Started")
            print(f"   Host: {self.host}")
            print(f"   Port: {self.port}")
            print(f"   Waiting for {self.target_clients} clients...")
            print("=" * 50)
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"📡 New connection from {address}")
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"❌ Server error: {e}")
                        
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        client_id = f"Client_{address[0]}_{address[1]}"
        
        try:
            while self.running:
                # Receive message from client
                message = self.receive_message(client_socket)
                if not message:
                    break
                
                if message['type'] == 'register':
                    self.register_client(client_id, message, client_socket)
                    
                elif message['type'] == 'weights':
                    self.receive_weights(client_id, message)
                    
                elif message['type'] == 'ping':
                    self.send_message(client_socket, {'type': 'pong'})
                    
        except Exception as e:
            print(f"❌ Error handling client {client_id}: {e}")
        finally:
            client_socket.close()
            if client_id in self.clients:
                del self.clients[client_id]
                print(f"🔌 Client {client_id} disconnected")
    
    def register_client(self, client_id, message, client_socket):
        """Register a new client"""
        self.clients[client_id] = {
            'socket': client_socket,
            'info': message.get('info', {}),
            'registered_at': datetime.now().isoformat()
        }
        
        print(f"✅ Client registered: {client_id}")
        print(f"   Samples: {message.get('info', {}).get('n_samples', 'Unknown')}")
        print(f"   Features: {message.get('info', {}).get('n_features', 'Unknown')}")
        
        # Send acknowledgment
        self.send_message(client_socket, {
            'type': 'registered',
            'client_id': client_id,
            'round': self.round_number
        })
        
        # Check if we have enough clients to start
        if len(self.clients) >= self.target_clients:
            print(f"🎯 Enough clients connected ({len(self.clients)}/{self.target_clients})")
            self.broadcast_start_training()
    
    def receive_weights(self, client_id, message):
        """Receive weights from a client"""
        try:
            # Decode weights from base64
            weights_data = message['weights']
            weights = pickle.loads(bytes.fromhex(weights_data))
            
            accuracy = message.get('accuracy', 0.0)
            samples = message.get('samples', 0)
            
            self.received_weights.append({
                'client_id': client_id,
                'weights': weights,
                'accuracy': accuracy,
                'samples': samples
            })
            
            print(f"📥 Received weights from {client_id}")
            print(f"   Local accuracy: {accuracy:.4f}")
            print(f"   Samples: {samples}")
            print(f"   Progress: {len(self.received_weights)}/{self.target_clients}")
            
            # Check if we have all weights
            if len(self.received_weights) >= self.target_clients:
                self.perform_federated_averaging()
                
        except Exception as e:
            print(f"❌ Error receiving weights from {client_id}: {e}")
    
    def perform_federated_averaging(self):
        """Perform federated averaging of received weights"""
        print(f"\n🔄 Performing Federated Averaging (Round {self.round_number + 1})...")
        
        # Extract weights and sample counts
        all_weights = []
        sample_counts = []
        
        for client_data in self.received_weights:
            all_weights.append(client_data['weights'])
            sample_counts.append(client_data['samples'])
        
        # Weighted averaging based on number of samples
        total_samples = sum(sample_counts)
        self.global_weights = np.zeros_like(all_weights[0])
        
        for weights, samples in zip(all_weights, sample_counts):
            weight_factor = samples / total_samples
            self.global_weights += weight_factor * weights
        
        print(f"✅ Federated averaging completed:")
        print(f"   Aggregated {len(all_weights)} client models")
        print(f"   Total samples: {total_samples}")
        print(f"   Global weights shape: {self.global_weights.shape}")
        
        # Send global weights to all clients
        self.broadcast_global_weights()
        
        # Prepare for next round
        self.received_weights = []
        self.round_number += 1
    
    def broadcast_start_training(self):
        """Tell all clients to start training"""
        message = {
            'type': 'start_training',
            'round': self.round_number
        }
        
        print(f"📢 Broadcasting start training for round {self.round_number}")
        for client_id, client_info in self.clients.items():
            try:
                self.send_message(client_info['socket'], message)
            except Exception as e:
                print(f"❌ Failed to send start training to {client_id}: {e}")
    
    def broadcast_global_weights(self):
        """Send global weights to all clients"""
        weights_hex = pickle.dumps(self.global_weights).hex()
        
        message = {
            'type': 'global_weights',
            'weights': weights_hex,
            'round': self.round_number
        }
        
        print(f"📤 Broadcasting global weights to {len(self.clients)} clients")
        for client_id, client_info in self.clients.items():
            try:
                self.send_message(client_info['socket'], message)
                print(f"   ✅ Sent to {client_id}")
            except Exception as e:
                print(f"   ❌ Failed to send to {client_id}: {e}")
    
    def send_message(self, client_socket, message):
        """Send a JSON message to a client"""
        try:
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            message_length = len(message_bytes)
            
            # Send message length first (4 bytes)
            client_socket.send(message_length.to_bytes(4, byteorder='big'))
            # Send actual message
            client_socket.send(message_bytes)
            
        except Exception as e:
            raise Exception(f"Failed to send message: {e}")
    
    def receive_message(self, client_socket):
        """Receive a JSON message from a client"""
        try:
            # Receive message length first (4 bytes)
            length_bytes = client_socket.recv(4)
            if len(length_bytes) != 4:
                return None
                
            message_length = int.from_bytes(length_bytes, byteorder='big')
            
            # Receive actual message
            message_bytes = b''
            while len(message_bytes) < message_length:
                chunk = client_socket.recv(min(4096, message_length - len(message_bytes)))
                if not chunk:
                    return None
                message_bytes += chunk
            
            message_json = message_bytes.decode('utf-8')
            return json.loads(message_json)
            
        except Exception as e:
            print(f"❌ Error receiving message: {e}")
            return None
    
    def cleanup(self):
        """Clean up server resources"""
        print("\n🧹 Cleaning up server...")
        self.running = False
        
        # Close all client connections
        for client_id, client_info in self.clients.items():
            try:
                client_info['socket'].close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("✅ Server cleanup completed")

def main():
    """Main function to run the aggregator server"""
    print("🎉 FEDERATED LEARNING AGGREGATOR")
    print("=" * 50)
    
    # Configuration
    HOST = input("Enter server host (default: localhost): ").strip() or "localhost"
    PORT = input("Enter server port (default: 8080): ").strip() or "8080"
    CLIENTS = input("Enter number of clients to wait for (default: 3): ").strip() or "3"
    
    try:
        PORT = int(PORT)
        CLIENTS = int(CLIENTS)
    except ValueError:
        print("❌ Invalid port or client number")
        return
    
    # Create and start aggregator
    aggregator = FederatedAggregator(host=HOST, port=PORT, target_clients=CLIENTS)
    
    try:
        aggregator.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server interrupted by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        aggregator.cleanup()

if __name__ == "__main__":
    main()
