#!/bin/bash
# Distributed Federated Learning Setup Script

echo "🚀 Setting up Distributed Federated Learning..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
chmod +x aggregator_server.py
chmod +x federated_client.py
chmod +x network_demo.py

echo "✅ Setup complete!"
echo ""
echo "🎯 Available Commands:"
echo ""
echo "1. Run Local Demo (all on one machine):"
echo "   python network_demo.py --local"
echo ""
echo "2. Run Distributed Setup:"
echo "   Server: python aggregator_server.py"
echo "   Client: python federated_client.py"
echo ""
echo "3. Run Original Demo:"
echo "   python federated_demo.py"
echo ""
echo "📖 See README.md for detailed instructions"
