import argparse
import threading
import time
import encoder  
import network_noise_generator  

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Main script for controlling network operations")
    parser.add_argument("action", choices=["start_noise", "send_message"], help="Action to perform: start_noise or send_message")
    parser.add_argument("destination_ip", help="Destination IP address")
    parser.add_argument("destination_port", type=int, help="Destination port number")
    parser.add_argument("--message", help="Message to send (required for send_message)", default="")

    args = parser.parse_args()

    if args.action == "start_noise":
        # Start the network noise generator
        start_network_noise(args.destination_ip, args.destination_port)
        # Keep the script running to allow the noise generator to continue
        print("Press Ctrl+C to stop the network noise generator.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nNetwork noise generator stopped by user.")
    
    elif args.action == "send_message":
        # Check if a message is provided for the send_message action
        if not args.message:
            print("Error: --message is required for sending an encoded message.")
        else:
            # Send the encoded message
            send_encoded_message(args.destination_ip, args.destination_port, args.message)

# For localhost testing
# python network_noise_generator.py 127.0.0.1 8080 --server (Start the HTTP server and background noise generator)
# python network_noise_generator.py 127.0.0.1 8080 (Run just the noise generator without the server)
# python main.py send_message 127.0.0.1 8080 --message "Hello, this is a covert message"

# For local testing
# python main.py start_noise 192.168.1.10 80
# python main.py send_message 192.168.1.10 80 --message "Testing message over HTTP port"

# For external testing
# python main.py start_noise 8.8.8.8 80
# python main.py send_message 8.8.8.8 80 --message "Hello, world"



