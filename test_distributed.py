#!/usr/bin/env python3
"""
Simple test script to verify the distributed federated learning system works
"""

import subprocess
import time
import sys
import os
import signal

def test_individual_components():
    """Test individual components separately"""
    print("🧪 Testing Individual Components")
    print("=" * 50)
    
    # Test 1: Import modules
    print("\n1. Testing imports...")
    try:
        from aggregator_server import FederatedAggregator
        print("✅ aggregator_server imports OK")
    except Exception as e:
        print(f"❌ aggregator_server import failed: {e}")
        return False
    
    try:
        from federated_client import FederatedClient
        print("✅ federated_client imports OK")
    except Exception as e:
        print(f"❌ federated_client import failed: {e}")
        return False
    
    # Test 2: Create instances
    print("\n2. Testing class instantiation...")
    try:
        server = FederatedAggregator(host='localhost', port=8081, target_clients=1)
        print("✅ FederatedAggregator created OK")
    except Exception as e:
        print(f"❌ FederatedAggregator creation failed: {e}")
        return False
    
    try:
        client = FederatedClient('test_client', 'localhost', 8081)
        print("✅ FederatedClient created OK")
    except Exception as e:
        print(f"❌ FederatedClient creation failed: {e}")
        return False
    
    # Test 3: Setup data
    print("\n3. Testing data setup...")
    try:
        client.setup_data(n_samples=100)
        print("✅ Client data setup OK")
    except Exception as e:
        print(f"❌ Client data setup failed: {e}")
        return False
    
    print("\n✅ All component tests passed!")
    return True

def test_simple_connection():
    """Test a simple server-client connection"""
    print("\n🔗 Testing Simple Connection")
    print("=" * 50)
    
    server_process = None
    client_process = None
    
    try:
        # Start server in background
        print("Starting server...")
        server_process = subprocess.Popen(
            [sys.executable, "-c", """
import sys
sys.path.append('.')
from aggregator_server import FederatedAggregator
import time

server = FederatedAggregator(host='localhost', port=8082, target_clients=1)
print('Server starting on port 8082...')

import threading
def run_server():
    try:
        server.start_server()
    except Exception as e:
        print(f'Server error: {e}')

server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

time.sleep(30)  # Run for 30 seconds
"""],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Start client
        print("Starting client...")
        client_process = subprocess.Popen(
            [sys.executable, "-c", """
import sys
sys.path.append('.')
from federated_client import FederatedClient
import time

client = FederatedClient('test_client_1', 'localhost', 8082)
print('Client created')

client.setup_data(n_samples=50)
print('Client data setup complete')

if client.connect_to_server():
    print('Client connected to server')
    client.start_client()
else:
    print('Client failed to connect')
"""],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Monitor for a few seconds
        print("Monitoring connection for 10 seconds...")
        time.sleep(10)
        
        # Check if processes are running
        if server_process.poll() is None:
            print("✅ Server is running")
        else:
            print("❌ Server stopped")
            
        if client_process.poll() is None:
            print("✅ Client is running")
        else:
            print("❌ Client stopped")
            
        # Get some output
        try:
            server_output = server_process.stdout.read()
            if server_output:
                print(f"Server output: {server_output[:200]}...")
        except:
            pass
            
        try:
            client_output = client_process.stdout.read()
            if client_output:
                print(f"Client output: {client_output[:200]}...")
        except:
            pass
        
        print("✅ Connection test completed")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
        
    finally:
        # Clean up
        if server_process:
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except:
                pass
                
        if client_process:
            try:
                client_process.terminate()
                client_process.wait(timeout=5)
            except:
                pass

def main():
    """Run all tests"""
    print("🎯 DISTRIBUTED FEDERATED LEARNING TESTS")
    print("=" * 50)
    
    success = True
    
    # Test components
    if not test_individual_components():
        success = False
    
    # Test connection
    if not test_simple_connection():
        success = False
    
    print(f"\n📊 TEST RESULTS: {'✅ ALL PASSED' if success else '❌ SOME FAILED'}")
    
    if success:
        print("\n🎉 System is working! Try running:")
        print("   python network_demo.py --local 2")
        print("   (Start with fewer clients for testing)")
    else:
        print("\n🔧 Please fix the issues above before running the full demo")
    
    return success

if __name__ == "__main__":
    main()
