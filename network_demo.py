#!/usr/bin/env python3
"""
Network Distributed Federated Learning Demo
Demonstrates how to run distributed federated learning across multiple machines
"""

import subprocess
import time
import sys
import os
import threading
import signal

class NetworkFederatedDemo:
    def __init__(self):
        self.server_process = None
        self.client_processes = []
        self.running = False
        
    def start_server(self, host='localhost', port=8080, n_clients=3):
        """Start the aggregator server"""
        print(f"🎯 Starting Aggregator Server...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Expected clients: {n_clients}")
        
        # Create server script
        server_script = f'''
import sys
sys.path.append('.')
from aggregator_server import FederatedAggregator

try:
    aggregator = FederatedAggregator(host="{host}", port={port}, target_clients={n_clients})
    print("Starting aggregator server...")
    aggregator.start_server()
except Exception as e:
    print(f"Server error: {{e}}")
    import traceback
    traceback.print_exc()
'''
        
        # Write temporary server script
        with open("temp_server.py", 'w') as f:
            f.write(server_script)
        
        # Start server process
        self.server_process = subprocess.Popen(
            [sys.executable, "temp_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor server startup
        time.sleep(2)
        return True
    
    def start_client(self, client_id, host='localhost', port=8080):
        """Start a federated learning client"""
        print(f"🤖 Starting Client: {client_id}")
        
        # Create a simple client script
        client_script = f'''
import sys
sys.path.append('.')
from federated_client import FederatedClient
import time

try:
    client = FederatedClient("{client_id}", "{host}", {port})
    client.setup_data()
    
    if client.connect_to_server():
        print("Client {client_id} connected successfully")
        client.start_client()
    else:
        print("Client {client_id} failed to connect")
        
except Exception as e:
    print(f"Client {client_id} error: {{e}}")
    import traceback
    traceback.print_exc()
'''
        
        # Write temporary client script
        script_path = f"temp_client_{client_id}.py"
        with open(script_path, 'w') as f:
            f.write(client_script)
        
        # Start client process
        client_process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        self.client_processes.append((client_id, client_process))
        return client_process
    
    def monitor_process(self, process, name):
        """Monitor a process output"""
        try:
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    print(f"[{name}] {line.strip()}")
                time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error monitoring {name}: {e}")
    
    def run_local_demo(self, n_clients=3):
        """Run a complete demo on local machine"""
        print("🎉 DISTRIBUTED FEDERATED LEARNING DEMO")
        print("=" * 50)
        
        self.running = True
        
        try:
            # Start server
            if not self.start_server('localhost', 8080, n_clients):
                return
            
            # Start server monitor
            server_monitor = threading.Thread(
                target=self.monitor_process,
                args=(self.server_process, "SERVER")
            )
            server_monitor.daemon = True
            server_monitor.start()
            
            # Wait for server to start
            time.sleep(3)
            
            # Start clients
            for i in range(n_clients):
                client_id = f"client_{i+1}"
                client_process = self.start_client(client_id, 'localhost', 8080)
                
                # Start client monitor
                client_monitor = threading.Thread(
                    target=self.monitor_process,
                    args=(client_process, f"CLIENT-{client_id}")
                )
                client_monitor.daemon = True
                client_monitor.start()
                
                time.sleep(2)  # Stagger client starts
            
            print(f"\n🚀 Demo running with {n_clients} clients...")
            print("   Press Ctrl+C to stop")
            
            # Wait for completion or interruption
            while self.running:
                time.sleep(1)
                
                # Check if server is still running
                if self.server_process.poll() is not None:
                    print("🏁 Server process completed")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
        except Exception as e:
            print(f"❌ Demo error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up all processes"""
        print("\n🧹 Cleaning up processes...")
        self.running = False
        
        # Terminate clients
        for client_id, client_process in self.client_processes:
            try:
                if client_process.poll() is None:
                    client_process.terminate()
                    client_process.wait(timeout=5)
                    print(f"✅ Stopped client {client_id}")
            except Exception as e:
                print(f"❌ Error stopping client {client_id}: {e}")
        
        # Terminate server
        if self.server_process:
            try:
                if self.server_process.poll() is None:
                    self.server_process.terminate()
                    self.server_process.wait(timeout=5)
                    print("✅ Stopped server")
            except Exception as e:
                print(f"❌ Error stopping server: {e}")
        
        # Clean up temporary files
        import os
        for i in range(1, 10):  # Clean up temp files
            for filename in [f"temp_client_client_{i}.py", "temp_server.py"]:
                if os.path.exists(filename):
                    os.remove(filename)
        
        print("✅ Cleanup completed")

def print_usage():
    """Print usage instructions"""
    print("📖 USAGE INSTRUCTIONS")
    print("=" * 50)
    print()
    print("🎯 Option 1: Run Local Demo (All on one machine)")
    print("   python network_demo.py --local")
    print()
    print("🌐 Option 2: Run Distributed (Multiple machines)")
    print("   On Server Machine:")
    print("   python aggregator_server.py")
    print()
    print("   On Each Client Machine:")
    print("   python federated_client.py")
    print()
    print("📋 Configuration Files:")
    print("   - aggregator_server.py: Central coordinator")
    print("   - federated_client.py: Individual participants")
    print("   - network_demo.py: Local testing script")
    print()
    print("🔧 Network Setup:")
    print("   - Server listens on specified host:port")
    print("   - Clients connect to server's IP and port")
    print("   - Ensure firewalls allow the communication")
    print()
    print("💡 Tips:")
    print("   - Use real IP addresses for distributed setup")
    print("   - Check network connectivity between machines")
    print("   - Start server before clients")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--local":
        # Run local demo
        demo = NetworkFederatedDemo()
        
        n_clients = 3
        if len(sys.argv) > 2:
            try:
                n_clients = int(sys.argv[2])
            except ValueError:
                print("❌ Invalid number of clients")
                return
        
        demo.run_local_demo(n_clients)
    else:
        # Print usage
        print_usage()

if __name__ == "__main__":
    main()
