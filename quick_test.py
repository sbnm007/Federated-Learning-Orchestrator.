#!/usr/bin/env python3
"""
Quick test of the distributed federated learning system
"""

import time
import threading
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def test_system():
    """Test the distributed system"""
    print("🎯 Testing Distributed Federated Learning System")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from aggregator_server import FederatedAggregator
        from federated_client import FederatedClient
        print("✅ Imports successful")
        
        # Test server creation
        print("2. Testing server creation...")
        server = FederatedAggregator(host='localhost', port=8083, target_clients=1)
        print("✅ Server created")
        
        # Test client creation
        print("3. Testing client creation...")
        client = FederatedClient('test_client', 'localhost', 8083)
        client.setup_data(n_samples=50)
        print("✅ Client created and data setup")
        
        # Test server start in thread
        print("4. Testing server start...")
        server_thread = threading.Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        print("✅ Server started")
        
        # Test client connection
        print("5. Testing client connection...")
        connected = client.connect_to_server()
        if connected:
            print("✅ Client connected successfully")
            
            # Test client operation for a few seconds
            print("6. Testing client operation...")
            client_thread = threading.Thread(target=client.start_client)
            client_thread.daemon = True
            client_thread.start()
            
            time.sleep(5)
            print("✅ Client operation test completed")
            
        else:
            print("❌ Client failed to connect")
            return False
            
        print("\n🎉 All tests passed! The system is working.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            if 'client' in locals():
                client.cleanup()
            if 'server' in locals():
                server.cleanup()
        except:
            pass

if __name__ == "__main__":
    success = test_system()
    
    if success:
        print("\n🚀 Ready to run distributed federated learning!")
        print("Try these commands:")
        print("   python network_demo.py --local 2")
        print("   python aggregator_server.py (in one terminal)")
        print("   python federated_client.py (in another terminal)")
    else:
        print("\n🔧 Please check the setup and fix any issues.")
        
    sys.exit(0 if success else 1)
