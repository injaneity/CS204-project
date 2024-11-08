import argparse
import threading
import time
import encoder 
import network_noise_generator 
import decoder  
from scapy.all import sniff 

def start_network_noise(destination_ip, destination_port):
    """Function to start the network noise generator in a separate thread."""
    noise_thread = threading.Thread(target=network_noise_generator.simulate_background_noise, args=(destination_ip, destination_port))
    noise_thread.daemon = True  # Set as a daemon so it ends when the main program ends
    noise_thread.start()
    print("Network noise generator started.")
    return noise_thread

def send_encoded_message(destination_ip, destination_port, message):
    """Function to send an encoded message."""
    print(f"Sending encoded message to {destination_ip}:{destination_port}")
    encoder.send_covert_message(destination_ip, destination_port, message)
    print("Encoded message sent successfully.")

def decode_message(port, timeout):
    """Function to capture and decode packets to retrieve the covert message."""
    print(f"Sniffing packets on port {port} for {timeout} seconds...")
    try:
        captured_packets = sniff(filter=f"tcp port {port}", timeout=timeout)
        message = decoder.decode_covert_message(captured_packets)
        print("Decoded Message:", message)
    except KeyboardInterrupt:
        print("\nSniffing interrupted by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Main script for controlling network operations")
    parser.add_argument("action", choices=["start_noise", "send_message", "decode"], help="Action to perform: start_noise, send_message, or decode")
    parser.add_argument("destination_ip", nargs='?', help="Destination IP address")
    parser.add_argument("destination_port", type=int, nargs='?', help="Destination port number (required for decode)")
    parser.add_argument("--message", help="Message to send (required for send_message)", default="")
    parser.add_argument("--timeout", type=int, help="Sniffing duration in seconds for decoding (default: 30)", default=30)

    args = parser.parse_args()

    if args.action == "start_noise":
        if args.destination_ip and args.destination_port:
            start_network_noise(args.destination_ip, args.destination_port)
            print("Press Ctrl+C to stop the network noise generator.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nNetwork noise generator stopped by user.")
        else:
            print("Error: Destination IP and port are required for starting network noise.")

    elif args.action == "send_message":
        if args.destination_ip and args.destination_port and args.message:
            send_encoded_message(args.destination_ip, args.destination_port, args.message)
        else:
            print("Error: Destination IP, port, and --message are required for sending an encoded message.")

    elif args.action == "decode":
        if args.destination_port is not None:
            decode_message(args.destination_port, args.timeout)
        else:
            print("Error: Port is required for decoding.")


# For localhost testing
# python network_noise_generator.py 127.0.0.1 8080 --server (Start the HTTP server and background noise generator)
# python network_noise_generator.py 127.0.0.1 8080 (Run just the noise generator without the server)
# python main.py send_message 127.0.0.1 8080 --message "Hello, this is a covert message"
# python main.py decode 127.0.0.1 8080 --timeout 30

# For local testing
# python main.py start_noise 192.168.1.10 80
# python main.py send_message 192.168.1.10 80 --message "Testing message over HTTP port"

# For external testing
# python main.py start_noise 8.8.8.8 80
# python main.py send_message 8.8.8.8 80 --message "Hello, world"



