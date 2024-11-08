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

def generate_random_http_traffic(destination_ip, destination_port):
    """Generate random HTTP GET requests to simulate traffic."""
    http_methods = ['GET', 'POST', 'HEAD']
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0)',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X)'
    ]

    while True:
        ip = IP(dst=destination_ip)
        tcp = TCP(sport=random.randint(1024, 65535), dport=destination_port, flags='PA')
        http_payload = f"{random.choice(http_methods)} / HTTP/1.1\r\nHost: {destination_ip}\r\nUser-Agent: {random.choice(user_agents)}\r\n\r\n"
        pkt = ip / tcp / Raw(load=http_payload)
        
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.1, 1.5))  # Add realistic delays between packets

def generate_random_tcp_connections(destination_ip, destination_port):
    """Generate random TCP connections to simulate network noise."""
    while True:
        ip = IP(dst=destination_ip)
        tcp = TCP(sport=random.randint(1024, 65535), dport=destination_port, flags='S')
        pkt = ip / tcp
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.05, 0.3))  # Random delay to simulate varying traffic frequency

def simulate_background_noise(destination_ip, destination_port):
    """Start multiple threads to generate background network noise."""
    num_threads = 5  # Number of traffic generation threads
    threads = []

    for _ in range(num_threads):
        t1 = threading.Thread(target=generate_random_http_traffic, args=(destination_ip, destination_port))
        # t2 = threading.Thread(target=generate_random_tcp_connections, args=(destination_ip, destination_port))
        t1.daemon = True
        # t2.daemon = True
        # threads.extend([t1, t2])
        threads.extend([t1])

    for t in threads:
        t.start()

    # Keep the main thread alive while noise is being generated
    while True:
        time.sleep(1)

def start_noise(destination_ip, destination_port, server=False):
    """Start network noise generation, optionally with an HTTP server."""
    if server:
        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=start_http_server, args=(('0.0.0.0', destination_port),))
        server_thread.daemon = True
        server_thread.start()
        print("HTTP server started for noise generation.")

    # Start background noise generation
    noise_thread = threading.Thread(target=simulate_background_noise, args=(destination_ip, destination_port))
    noise_thread.daemon = True
    noise_thread.start()
    print(f"Background noise generation started for {destination_ip}:{destination_port}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Background Network Noise Generator with HTTP Server")
    parser.add_argument("destination_ip", help="Destination IP address")
    parser.add_argument("destination_port", type=int, help="Destination port number")
    parser.add_argument("--server", action="store_true", help="Start an HTTP server to handle incoming traffic")
    args = parser.parse_args()

    if args.server:
        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=start_http_server, args=(('0.0.0.0', args.destination_port),))
        server_thread.daemon = True
        server_thread.start()
        print("HTTP server started for noise generation.")

    print(f"Starting background noise generation for {args.destination_ip}:{args.destination_port}")
    simulate_background_noise(args.destination_ip, args.destination_port)
