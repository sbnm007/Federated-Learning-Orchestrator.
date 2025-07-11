# Federated Learning Orchestrator

A complete implementation of a federated learning system that 📊 FEDERATED LEARNING RESULTS:
   Average Local Accuracy:  0.8333
   Average Global Accuracy: 0.8611
   Overall Improvement:     0.0278
```strates how multiple nodes can collaborate to train machine learning models without sharing raw data, preserving privacy while enabling collaborative learning.

## 🎯 Project Overview

This federated learning orchestrator implements:
- **Distributed Learning**: Multiple clients train models on their private data
- **Federated Averaging**: Combines model weights using the FedAvg algorithm
- **Privacy Preservation**: Only model weights are shared, never raw data
- **Real ML Integration**: Actual machine learning with scikit-learn

## 🏗️ Architecture

### Components
1. **federated_demo.py** - Complete federated learning demonstration (single machine)
2. **aggregator_server.py** - Central server for distributed federated learning
3. **federated_client.py** - Individual client nodes for distributed learning
4. **network_demo.py** - Network-based demonstration script
5. **setup_distributed.sh** - Setup script for distributed learning

### Federated Learning Process
1. **Data Distribution**: Each client has their own private dataset
2. **Local Training**: Clients train models independently on local data
3. **Weight Sharing**: Only model parameters are shared (not raw data)
4. **Federated Averaging**: Aggregator combines weights using FedAvg algorithm
5. **Global Model**: Improved model distributed back to all clients

### Two Operation Modes

#### 1. Single Machine Demo
- All clients simulated on one machine
- Good for learning and testing
- Uses `federated_demo.py`

#### 2. Distributed Network Setup
- Server and clients on different machines
- Real-world federated learning scenario
- Uses `aggregator_server.py` and `federated_client.py`

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment support

### Setup
```bash
# Navigate to project directory
cd Federated-Learning-Orchestrator

# Run the automated setup and demo
./run_demo.sh
```

### Running the Demo

#### Quick Start (Recommended)
```bash
# Run the automated setup and demo
./run_demo.sh
```

#### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the demo
python federated_demo.py
```

#### Advanced Options
```bash
# Run multi-round federated learning
python federated_demo.py --multi-round

# Run distributed setup
./setup_distributed.sh
```

### Distributed Network Setup

#### ✅ Working Local Network Demo
```bash
# Quick test to verify everything works
./venv/bin/python quick_test.py

# Simple local demo with multiple clients
./venv/bin/python simple_demo.py 3
```

#### Option 1: Manual Distributed Setup (Recommended)
```bash
# On Server Machine (Terminal 1)
source venv/bin/activate
python aggregator_server.py
# Enter: localhost (or your server IP)
# Enter: 8080 (or your preferred port)
# Enter: 3 (number of clients to wait for)

# On Client Machine 1 (Terminal 2)
source venv/bin/activate
python federated_client.py
# Enter: client_hospital_1
# Enter: localhost (or server IP)
# Enter: 8080

# On Client Machine 2 (Terminal 3)
source venv/bin/activate
python federated_client.py
# Enter: client_bank_1
# Enter: localhost (or server IP)
# Enter: 8080

# On Client Machine 3 (Terminal 4)
source venv/bin/activate
python federated_client.py
# Enter: client_research_1
# Enter: localhost (or server IP)
# Enter: 8080
```

#### Option 2: True Distributed Setup (Different Machines)
```bash
# On Server Machine (e.g., 192.168.1.100)
python aggregator_server.py
# Enter: 192.168.1.100, 8080, 3

# On Client Machine 1 (e.g., 192.168.1.101)
python federated_client.py
# Enter: client_1, 192.168.1.100, 8080

# On Client Machine 2 (e.g., 192.168.1.102)
python federated_client.py
# Enter: client_2, 192.168.1.100, 8080

# On Client Machine 3 (e.g., 192.168.1.103)
python federated_client.py
# Enter: client_3, 192.168.1.100, 8080
```

## 📊 What You'll See

### Demo Output
```
🎉 FEDERATED LEARNING DEMONSTRATION
==================================================
🔄 Setting up federated clients...
✅ Client_1: 240 training samples, 60 test samples
✅ Client_2: 240 training samples, 60 test samples
✅ Client_3: 240 training samples, 60 test samples

🤖 Starting local training...

📊 Training Client_1...
✅ Client_1 completed:
   Local accuracy: 0.8500
   Weights shape: (11,)

🔄 Performing Federated Averaging...
✅ Federated averaging completed:
   Aggregated 3 client models
   Global weights shape: (11,)

📈 Evaluating Global Model...
🎯 Client_1:
   Local accuracy:  0.8500
   Global accuracy: 0.8667
   Improvement:     0.0167

� FEDERATED LEARNING RESULTS:
   Average Local Accuracy:  0.8333
   Average Global Accuracy: 0.8611
   Overall Improvement:     0.0278
```

## 🛠️ Technical Details

### Dependencies
- **numpy**: Numerical computing for model weights
- **scikit-learn**: Machine learning algorithms
- **matplotlib**: Visualization of results

### Key Features
- **Privacy Preserving**: Only model weights are shared, never raw data
- **Distributed Learning**: Each client trains independently
- **Network Communication**: TCP sockets for reliable communication
- **Weighted Averaging**: FedAvg algorithm with sample-weighted aggregation
- **Real ML**: Actual machine learning with logistic regression
- **Scalable**: Can run on single machine or distributed across network

### Algorithm Details
1. **Data Generation**: Synthetic classification dataset split among clients
2. **Local Training**: Each client trains a LogisticRegression model
3. **Weight Extraction**: Model coefficients and intercept are extracted
4. **Federated Averaging**: Simple averaging of all client weights
5. **Global Evaluation**: Global model tested on each client's data

## 🔧 Customization

### Modifying the ML Model
Edit `federated_demo.py` to change:
```python
# Change model type
client['model'] = LogisticRegression(random_state=42, max_iter=1000)
# to
client['model'] = RandomForestClassifier(random_state=42)

# Change dataset parameters
X, y = make_classification(
    n_samples=900,          # Total samples
    n_features=10,          # Number of features
    n_informative=8,        # Informative features
    n_clusters_per_class=1, # Cluster complexity
    random_state=42
)
```

### Adding More Clients
```python
# Initialize with more clients
fl_demo = FederatedLearningDemo(n_clients=5)
```

### Changing Data Distribution
```python
# Non-uniform data distribution
client_sizes = [200, 300, 400]  # Different data sizes per client
```

## 🎓 Learning Outcomes

This project demonstrates:
1. **Federated Learning Concepts**: Privacy-preserving distributed ML
2. **Data Privacy**: How to collaborate without sharing raw data
3. **Model Aggregation**: Combining multiple models into one
4. **Performance Evaluation**: Comparing local vs global models
5. **Practical Implementation**: Real-world federated learning system

## 🤝 Use Cases

- **Healthcare**: Collaborative medical research without sharing patient data
- **Finance**: Fraud detection across institutions without sharing transactions
- **IoT**: Edge device learning without central data collection
- **Research**: Multi-institutional academic collaboration

## 🐛 Troubleshooting

### Common Issues
1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Virtual environment**: Ensure venv is activated with `source venv/bin/activate`
3. **Python version**: Requires Python 3.8+
4. **Display issues**: For headless systems, matplotlib may need backend configuration

### Debug Mode
Add more verbose logging by modifying the print statements in the code.

## 📈 Future Enhancements

Potential improvements:
- [ ] Neural network models (PyTorch/TensorFlow)
- [ ] Differential privacy implementation
- [ ] Non-IID data distribution
- [ ] Byzantine fault tolerance
- [ ] Performance benchmarking
- [ ] Web dashboard for monitoring
- [ ] Docker containerization

## 📖 References

- [Federated Learning Paper](https://arxiv.org/abs/1602.05629)
- [FedAvg Algorithm](https://arxiv.org/abs/1602.05629)
- [Scikit-learn Documentation](https://scikit-learn.org/)

## 🎉 Conclusion

This federated learning orchestrator provides a complete foundation for understanding and implementing federated learning systems. It combines theoretical concepts with practical implementation, making it perfect for education, research, and prototype development.

The demo shows how federated learning can improve model performance while maintaining data privacy - a crucial concept for modern distributed machine learning!

Happy federated learning! 🚀
