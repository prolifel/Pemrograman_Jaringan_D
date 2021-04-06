import sys
import socket

# Create a TCP/IP socket
sock_alpine_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_alpine_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address_alpine_1 = ('192.168.122.156', 10000)
server_address_alpine_2 = ('192.168.122.181', 10000)
print(f"connecting to {server_address_alpine_1}")
print(f"connecting to {server_address_alpine_2}")
sock_alpine_1.connect(server_address_alpine_1)
sock_alpine_2.connect(server_address_alpine_2)


try:
    # Send data image
    message = open("img.jpg", 'rb')
    message_read = message.read()
    print(f"sending {message}")
    sock_alpine_1.sendall(message_read)
    sock_alpine_2.sendall(message_read)

    # Look for the response alpine 1
    amount_received_alpine_1 = 0
    amount_expected_alpine_1 = len(message_read)
    file_alpine_1 = bytearray()
    while amount_received_alpine_1 < amount_expected_alpine_1:
        data_alpine_1 = sock_alpine_1.recv(16)
        amount_received_alpine_1 += len(data_alpine_1)
        file_alpine_1 += data_alpine_1
        print("dari alpine 1: ", f"{data_alpine_1}")
    
    # write file respon dari alpine 1
    write_alpine_1 = open("alpine1_img.jpg", 'wb')
    write_alpine_1.write(file_alpine_1)
    write_alpine_1.close()

    # Look for the response alpine 2
    amount_received_alpine_2 = 0
    amount_expected_alpine_2 = len(message_read)
    file_alpine_2 = bytearray()
    while amount_received_alpine_2 < amount_expected_alpine_2:
        data_alpine_2 = sock_alpine_2.recv(16)
        amount_received_alpine_2 += len(data_alpine_2)
        file_alpine_2 += data_alpine_2
        print("dari alpine 2: ", f"{data_alpine_2}")

    # write file respon dari alpine 2
    write_alpine_2 = open("alpine2_img.jpg", 'wb')
    write_alpine_2.write(file_alpine_2)
    write_alpine_2.close()
finally:
    print("closing")
    sock_alpine_1.close()
    sock_alpine_2.close()