#!/usr/bin/env python3
"""
Federated Learning Demonstration
A complete, working implementation of federated learning without complex P2P dependencies
"""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import time

class FederatedLearningDemo:
    def __init__(self, n_clients=3):
        self.n_clients = n_clients
        self.clients = []
        self.global_weights = None
        
    def setup_clients(self):
        """Create federated clients with different data distributions"""
        print("🔄 Setting up federated clients...")
        
        # Generate base dataset
        X, y = make_classification(
            n_samples=900,
            n_features=10,
            n_informative=8,
            n_redundant=2,
            n_clusters_per_class=1,
            random_state=42
        )
        
        # Split data among clients (simulating different organizations)
        samples_per_client = len(X) // self.n_clients
        
        for i in range(self.n_clients):
            start_idx = i * samples_per_client
            end_idx = (i + 1) * samples_per_client
            
            client_X = X[start_idx:end_idx]
            client_y = y[start_idx:end_idx]
            
            # Split into train/test
            X_train, X_test, y_train, y_test = train_test_split(
                client_X, client_y, test_size=0.2, random_state=42
            )
            
            client = {
                'id': f'Client_{i+1}',
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'weights': None,
                'local_accuracy': 0.0
            }
            
            self.clients.append(client)
            print(f"✅ {client['id']}: {len(X_train)} training samples, {len(X_test)} test samples")
    
    def local_training(self):
        """Each client trains on their local data"""
        print("\n🤖 Starting local training...")
        
        for client in self.clients:
            print(f"\n📊 Training {client['id']}...")
            
            # Train local model
            client['model'].fit(client['X_train'], client['y_train'])
            
            # Evaluate local model
            y_pred = client['model'].predict(client['X_test'])
            client['local_accuracy'] = accuracy_score(client['y_test'], y_pred)
            
            # Extract weights (coefficients + intercept)
            weights = np.concatenate([
                client['model'].coef_.flatten(),
                client['model'].intercept_
            ])
            client['weights'] = weights
            
            print(f"✅ {client['id']} completed:")
            print(f"   Local accuracy: {client['local_accuracy']:.4f}")
            print(f"   Weights shape: {weights.shape}")
            
            # Simulate training time
            time.sleep(0.5)
    
    def federated_averaging(self):
        """Aggregate weights from all clients using FedAvg"""
        print("\n🔄 Performing Federated Averaging...")
        
        # Collect all weights
        all_weights = [client['weights'] for client in self.clients]
        
        # Simple averaging (FedAvg algorithm)
        self.global_weights = np.mean(all_weights, axis=0)
        
        print(f"✅ Federated averaging completed:")
        print(f"   Aggregated {len(all_weights)} client models")
        print(f"   Global weights shape: {self.global_weights.shape}")
        print(f"   Sample global weights: {self.global_weights[:3]}")
        
        return self.global_weights
    
    def evaluate_global_model(self):
        """Evaluate the global model on all clients"""
        print("\n📈 Evaluating Global Model...")
        
        global_accuracies = []
        
        for client in self.clients:
            # Create a model with global weights
            global_model = LogisticRegression(random_state=42, max_iter=1000)
            global_model.fit(client['X_train'], client['y_train'])  # Fit to get shape
            
            # Set global weights
            n_features = client['X_train'].shape[1]
            global_model.coef_ = self.global_weights[:n_features].reshape(1, -1)
            global_model.intercept_ = self.global_weights[n_features:]
            
            # Evaluate on client's test data
            y_pred = global_model.predict(client['X_test'])
            global_accuracy = accuracy_score(client['y_test'], y_pred)
            global_accuracies.append(global_accuracy)
            
            print(f"🎯 {client['id']}:")
            print(f"   Local accuracy:  {client['local_accuracy']:.4f}")
            print(f"   Global accuracy: {global_accuracy:.4f}")
            print(f"   Improvement:     {global_accuracy - client['local_accuracy']:.4f}")
        
        avg_local = np.mean([c['local_accuracy'] for c in self.clients])
        avg_global = np.mean(global_accuracies)
        
        print(f"\n📊 FEDERATED LEARNING RESULTS:")
        print(f"   Average Local Accuracy:  {avg_local:.4f}")
        print(f"   Average Global Accuracy: {avg_global:.4f}")
        print(f"   Overall Improvement:     {avg_global - avg_local:.4f}")
        
        return global_accuracies
    
    def visualize_results(self, global_accuracies):
        """Create visualization of results"""
        print("\n📊 Creating visualization...")
        
        try:
            client_names = [client['id'] for client in self.clients]
            local_accuracies = [client['local_accuracy'] for client in self.clients]
            
            # Create comparison plot
            x = np.arange(len(client_names))
            width = 0.35
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Plot 1: Accuracy comparison
            ax1.bar(x - width/2, local_accuracies, width, label='Local Model', alpha=0.8, color='lightcoral')
            ax1.bar(x + width/2, global_accuracies, width, label='Global Model', alpha=0.8, color='lightblue')
            
            ax1.set_xlabel('Clients')
            ax1.set_ylabel('Accuracy')
            ax1.set_title('Local vs Global Model Accuracy')
            ax1.set_xticks(x)
            ax1.set_xticklabels(client_names)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Add value labels
            for i, (local, global_acc) in enumerate(zip(local_accuracies, global_accuracies)):
                ax1.text(i - width/2, local + 0.01, f'{local:.3f}', ha='center', va='bottom')
                ax1.text(i + width/2, global_acc + 0.01, f'{global_acc:.3f}', ha='center', va='bottom')
            
            # Plot 2: Weights visualization
            for i, client in enumerate(self.clients):
                ax2.plot(client['weights'][:8], 'o-', label=f'{client["id"]}', alpha=0.7)
            
            # Plot global weights
            ax2.plot(self.global_weights[:8], 'k--', linewidth=2, label='Global Weights', alpha=0.9)
            
            ax2.set_xlabel('Weight Index')
            ax2.set_ylabel('Weight Value')
            ax2.set_title('Model Weights Comparison (First 8 weights)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('federated_learning_results.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✅ Visualization saved as 'federated_learning_results.png'")
            
        except Exception as e:
            print(f"⚠️ Visualization failed: {e}")
            print("   (This is normal if running in a headless environment)")

def run_multiple_rounds():
    """Run multiple rounds of federated learning"""
    print("🎉 FEDERATED LEARNING DEMONSTRATION")
    print("=" * 50)
    
    # Initialize federated learning system
    fl_demo = FederatedLearningDemo(n_clients=3)
    
    # Setup clients with distributed data
    fl_demo.setup_clients()
    
    # Run multiple rounds
    for round_num in range(3):
        print(f"\n🔄 ROUND {round_num + 1}")
        print("-" * 30)
        
        # Each client trains locally
        fl_demo.local_training()
        
        # Aggregate weights using federated averaging
        global_weights = fl_demo.federated_averaging()
        
        # Evaluate global model
        global_accuracies = fl_demo.evaluate_global_model()
        
        # Update each client's model with global weights for next round
        for client in fl_demo.clients:
            n_features = client['X_train'].shape[1]
            client['model'].coef_ = global_weights[:n_features].reshape(1, -1)
            client['model'].intercept_ = global_weights[n_features:]
        
        if round_num < 2:  # Not the last round
            print("\n⏳ Preparing for next round...")
            time.sleep(1)
    
    # Final visualization
    fl_demo.visualize_results(global_accuracies)
    
    print("\n🎊 Multi-Round Federated Learning Complete!")
    print("=" * 50)

def main():
    """Main demonstration function"""
    print("🎉 FEDERATED LEARNING DEMONSTRATION")
    print("=" * 50)
    
    # Initialize federated learning system
    fl_demo = FederatedLearningDemo(n_clients=3)
    
    # Setup clients with distributed data
    fl_demo.setup_clients()
    
    # Each client trains locally
    fl_demo.local_training()
    
    # Aggregate weights using federated averaging
    global_weights = fl_demo.federated_averaging()
    
    # Evaluate global model
    global_accuracies = fl_demo.evaluate_global_model()
    
    # Visualize results
    fl_demo.visualize_results(global_accuracies)
    
    print("\n🎊 Demonstration Complete!")
    print("=" * 50)
    print("Key Concepts Demonstrated:")
    print("• Data remains distributed (privacy preserved)")
    print("• Only model weights are shared between clients")
    print("• Federated averaging improves overall performance")
    print("• No central data collection required")
    print("\nTry running with --multi-round for multiple training rounds!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--multi-round":
        run_multiple_rounds()
    else:
        main()
