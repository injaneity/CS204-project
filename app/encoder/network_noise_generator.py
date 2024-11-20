from scapy.all import *
import random
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import argparse

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP server handler to respond to incoming requests."""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>GET request received</h1></body></html>")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Received POST data: {post_data.decode()}")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>POST request received</h1></body></html>")

def start_http_server(server_address=('0.0.0.0', 8080)):
    """Start a simple HTTP server."""
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"HTTP server running on {server_address[0]}:{server_address[1]}")
    httpd.serve_forever()

stop_event = threading.Event()
threads = []

def generate_random_http_traffic(destination_ip, destination_port):
    """Generate random HTTP GET requests to simulate traffic."""
    http_methods = ['GET', 'POST', 'HEAD']
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0)',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X)'
    ]

    while not stop_event.is_set():
        ip = IP(dst=destination_ip)
        tcp = TCP(sport=random.randint(1024, 65535), dport=destination_port, flags='PA')
        http_payload = f"{random.choice(http_methods)} / HTTP/1.1\r\nHost: {destination_ip}\r\nUser-Agent: {random.choice(user_agents)}\r\n\r\n"
        pkt = ip / tcp / Raw(load=http_payload)
        
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.1, 1.5))  # Add realistic delays between packets

def simulate_background_noise(destination_ip, destination_port):
    """Start multiple threads to generate background network noise."""
    global threads
    num_threads = 5  # Number of traffic generation threads

    stop_event.clear()  # Ensure the event is cleared to allow the threads to run

    for _ in range(num_threads):
        t = threading.Thread(target=generate_random_http_traffic, args=(destination_ip, destination_port))
        t.daemon = True
        threads.append(t)

    for t in threads:
        t.start()

    print("Background noise generation started.")

def start_noise(destination_ip, destination_port, server=False):
    """Start network noise generation, optionally with an HTTP server."""
    if server:
        server_thread = threading.Thread(target=start_http_server, args=(('0.0.0.0', destination_port),))
        server_thread.daemon = True
        server_thread.start()
        print("HTTP server started for noise generation.")

    simulate_background_noise(destination_ip, destination_port)

def stop_noise():
    """Stop all background noise generation."""
    stop_event.set()
    for t in threads:
        t.join()  # Ensure all threads are stopped
    threads.clear()  # Clear the list to allow restarting
    print("Noise generation stopped.")

def toggle_noise(destination_ip, destination_port):
    """Toggle noise generation on or off."""
    if stop_event.is_set():
        print("Resuming noise generation...")
        start_noise(destination_ip, destination_port)
    else:
        print("Pausing noise generation...")
        stop_noise()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Background Network Noise Generator with HTTP Server")
    parser.add_argument("destination_ip", help="Destination IP address")
    parser.add_argument("destination_port", type=int, help="Destination port number")
    parser.add_argument("--server", action="store_true", help="Start an HTTP server to handle incoming traffic")
    args = parser.parse_args()

    if args.server:
        server_thread = threading.Thread(target=start_http_server, args=(('0.0.0.0', args.destination_port),))
        server_thread.daemon = True
        server_thread.start()
        print("HTTP server started for noise generation.")

    print(f"Starting background noise generation for {args.destination_ip}:{args.destination_port}")
    start_noise(args.destination_ip, args.destination_port)

    try:
        while True:
            command = input("Enter 'toggle' to start/stop noise or 'exit' to quit: ").strip().lower()
            if command == 'toggle':
                toggle_noise(args.destination_ip, args.destination_port)
            elif command == 'exit':
                stop_noise()
                break
    except KeyboardInterrupt:
        stop_noise()