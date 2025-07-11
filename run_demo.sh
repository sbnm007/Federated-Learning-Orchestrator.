#!/bin/bash
# Quick setup and run script for Federated Learning Orchestrator

echo "🚀 Setting up Federated Learning Orchestrator..."

# # Remove old virtual environment if it exists
# if [ -d "venv" ]; then
#     echo "🧹 Removing old virtual environment..."
#     rm -rf venv
# fi

# # Create fresh virtual environment
# echo "📦 Creating virtual environment..."
# python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install build tools
echo "⬆️ Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🎉 Running Federated Learning Demo..."
echo "="*50

# Run the demo
python federated_demo.py

echo ""
echo "✅ Demo completed successfully!"
echo ""
echo "🎊 Next Steps:"
echo "• Try: python federated_demo.py --multi-round"
echo "• Check the generated visualization: federated_learning_results.png"
echo "• Explore the code in federated_demo.py"
