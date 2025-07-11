#!/usr/bin/env python3
"""
Simple Local Federated Learning Demo
Runs multiple clients and server on the same machine for testing
"""

import subprocess
import time
import sys
import os
import threading
import signal

def run_simple_local_demo(n_clients=3):
    """Run a simple local demo with multiple clients"""
    print(f"🎉 LOCAL FEDERATED LEARNING DEMO")
    print("=" * 50)
    print(f"Running with {n_clients} clients on localhost")
    
    # Use the virtual environment Python
    venv_python = "/home/sibin/Projects/Federated-Learning-Orchestrator./venv/bin/python"
    
    server_process = None
    client_processes = []
    
    try:
        # Start server
        print("🎯 Starting aggregator server...")
        server_env = os.environ.copy()
        server_env['PYTHONPATH'] = os.getcwd()
        
        server_process = subprocess.Popen([
            venv_python, '-c', f'''
import sys
import os
sys.path.insert(0, os.getcwd())
from aggregator_server import FederatedAggregator

server = FederatedAggregator(host="localhost", port=8084, target_clients={n_clients})
print("Server ready on localhost:8084")
server.start_server()
'''
        ], env=server_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Wait for server to start
        time.sleep(3)
        
        # Start clients
        for i in range(n_clients):
            client_id = f"client_{i+1}"
            print(f"🤖 Starting {client_id}...")
            
            client_env = os.environ.copy()
            client_env['PYTHONPATH'] = os.getcwd()
            
            client_process = subprocess.Popen([
                venv_python, '-c', f'''
import sys
import os
sys.path.insert(0, os.getcwd())
from federated_client import FederatedClient
import time

client = FederatedClient("{client_id}", "localhost", 8084)
client.setup_data(n_samples=100 + {i}*50)  # Different data sizes

if client.connect_to_server():
    print("{client_id} connected successfully")
    client.start_client()
else:
    print("{client_id} failed to connect")
'''
            ], env=client_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            client_processes.append((client_id, client_process))
            time.sleep(1)  # Stagger client starts
        
        print(f"\n🚀 Demo running with server and {n_clients} clients...")
        print("📊 Monitoring federated learning progress...")
        print("   Press Ctrl+C to stop")
        
        # Monitor output from server and clients
        def monitor_process(process, name):
            try:
                while process.poll() is None:
                    line = process.stdout.readline()
                    if line.strip():
                        print(f"[{name}] {line.strip()}")
                    time.sleep(0.1)
            except:
                pass
        
        # Start monitoring threads
        threads = []
        
        # Monitor server
        server_thread = threading.Thread(target=monitor_process, args=(server_process, "SERVER"))
        server_thread.daemon = True
        server_thread.start()
        threads.append(server_thread)
        
        # Monitor clients
        for client_id, client_process in client_processes:
            client_thread = threading.Thread(target=monitor_process, args=(client_process, f"CLIENT-{client_id}"))
            client_thread.daemon = True
            client_thread.start()
            threads.append(client_thread)
        
        # Wait for completion or interruption
        start_time = time.time()
        while time.time() - start_time < 60:  # Run for max 60 seconds
            time.sleep(1)
            
            # Check if all processes completed
            all_done = True
            if server_process.poll() is None:
                all_done = False
            for _, client_process in client_processes:
                if client_process.poll() is None:
                    all_done = False
            
            if all_done:
                print("🎉 All processes completed successfully!")
                break
        
        print("✅ Demo completed!")
        
    except KeyboardInterrupt:
        print("\\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        # Cleanup
        print("🧹 Cleaning up processes...")
        
        # Stop clients
        for client_id, client_process in client_processes:
            try:
                if client_process.poll() is None:
                    client_process.terminate()
                    client_process.wait(timeout=3)
                print(f"✅ Stopped {client_id}")
            except:
                pass
        
        # Stop server
        if server_process:
            try:
                if server_process.poll() is None:
                    server_process.terminate()
                    server_process.wait(timeout=3)
                print("✅ Stopped server")
            except:
                pass
        
        print("✅ Cleanup completed")

def main():
    """Main function"""
    n_clients = 3
    if len(sys.argv) > 1:
        try:
            n_clients = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid number of clients")
            return
    
    run_simple_local_demo(n_clients)

if __name__ == "__main__":
    main()
