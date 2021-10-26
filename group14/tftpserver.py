"""
- CS2911 - 051
- Fall 2021
- Lab 07
- Names:
  - Elisha Hamp
  - Josiah Clausen

A Trivial File Transfer Protocol Server

Introduction:
Introduces us students to TFTP. This is accomplished by having us a create a TFTP server that is capable
of receiving a GET request, handling sending a file in blocks, and properly responding to acknowledgement packages.

Summary:
This lab was a fun one due to the rfc being so short, it allowed for a fairly straightforward implementation
of all the desired features. The best part of the lab was reading about the different packets, as the documentation
was very easy to understand. The worst part was our own understanding of how to use the UDP sending and receiving
functions. One change which we could recommend is some better way for us to test a socket timeout.

"""

# import modules -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket
import os
import math

# Helpful constants used by TFTP
from os.path import exists

TFTP_PORT = 69
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65536


def main():
    """
    Processes a single TFTP request
    """

    client_socket = socket_setup()

    print("Server is ready to receive a request")

    message, address = receive_request(client_socket)
    op_code, file_name, mode, error = parse_request(message)
    if not error:
        read_file(file_name, client_socket, address)
    else:
        send_error(client_socket, address, 1)

    client_socket.close()


def get_file_block_count(filename):
    """
    Determines the number of TFTP blocks for the given file
    :param filename: THe name of the file
    :return: The number of TFTP blocks for the file or -1 if the file does not exist
    """
    try:
        # Use the OS call to get the file size
        # This function throws an exception if the file doesn't exist
        file_size = os.stat(filename).st_size
        return math.ceil(file_size / TFTP_BLOCK_SIZE)
    except:
        return -1


def get_file_block(filename, block_number):
    """
    Get the file block data for the given file and block number
    :param filename: The name of the file to read
    :param block_number: The block number (1 based)
    :return: The data contents (as a bytes object) of the file block
    """
    file = open(filename, 'rb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    block_data = file.read(TFTP_BLOCK_SIZE)
    file.close()
    return block_data


def put_file_block(filename, block_data, block_number):
    """
    Writes a block of data to the given file
    :param filename: The name of the file to save the block to
    :param block_data: The bytes object containing the block data
    :param block_number: The block number (1 based)
    :return: Nothing
    """
    file = open(filename, 'wb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    file.write(block_data)
    file.close()


def socket_setup():
    """
    Sets up a UDP socket to listen on the TFTP port
    :return: The created socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', TFTP_PORT))
    return s


def receive_request(request_socket):
    """
    This method receives the request from a client using UDP and gets the
    address as well as the message
    :param request_socket: the socket that is used to receive from the client
    TFTP
    :return: the request from the client in bytes
    """
    byte, address = request_socket.recvfrom(MAX_UDP_PACKET_SIZE)
    return byte, address


def parse_request(request):
    """
    Gets the request and determines what to do with it
    :param request:
    :return: the opcode of the packet and whether it is an error request.
    it also returns the file name mode as well as if it needs to throw an error
    """
    op_code = 5
    file_name = b''
    mode = b''
    error = False
    if verify_request(request):
        print(str(type) + "THIS IS THE FIRST BYTE")
        op_code = 1
        code = request.replace(b'\x00\01', b'')
        print("GETFILE HAS BEEN CHOSEN")
        file_name = code[0: code.index(b'\x00')]
        print(file_name)
        code = code.replace(file_name + b'\x00', b'')
        mode = code[0: code.index(b'\x00')]
        print(mode)
    else:
        error = True
    return op_code, file_name, mode, error


def verify_request(request_line):
    """
    This method checks if the request line is a read request and that it has
    the proper amount of breaks in it
    :param request_line:
    :return: a boolean on weather the request is a valid read request
    """
    is_request = True
    if request_line.count(b'\x00') != 3:
        is_request = False
    req_type = request_line[0: 2]
    if req_type != b'\x00\x01':
        is_request = False
    return is_request


def send_error(client_socket, address, error_code):
    """
    This method is designed to send an error to the client if something goes wrong
    it can send three errors right now. If the user enters a request that is not
    covered. If the user tries to get a file that does not exist or we don't have
    access to. Finally a error for any unexpected problems
    :param client_socket: the client socket that the error will be send to
    :param address: the address to know where the request came from
    :param error_code: the code given by the program to tell which error it is
    """
    if error_code == 1:
        client_socket.sendto(b'\x00\x05\x00\x04\x40The '
                             b'request was invalid or not covered by this server\x00', address)
    elif error_code == 2:
        client_socket.sendto(b'\x00\x05\x00\x01\x40The file you requested does not exist\x00', address)
    else:
        client_socket.sendto(b'\x00\x05\x00\x00\x40Something went wrong we dont know what\x00', address)


def read_file(file_name, client_socket, address):
    """
    :author: Elisha Hamp
    Takes in a file_name and uses it to learn how many blocks are in the file before sending it.
    :param file_name: file requested by the client
    :param client_socket: socket of the client
    :param address: address received from the client
    """
    file_exist = exists(file_name)
    if file_exist:
        send_file(file_name, client_socket, address)
    else:
        send_error(client_socket, address, 2)


def send_file(file_name, client_socket, address):
    """
    :author: Elisha Hamp
    Uses the requested file name to create blocks, ensuring that each one gets sent.
    :param file_name: Name of the client selected file.
    :param client_socket: the socket of the client that made the request
    :param address: address received from receiving bytes from the client
    """
    num_blocks = get_file_block_count(file_name)
    i = 1
    while i <= num_blocks:
        block = get_file_block(file_name, i)
        send_block(i, block, client_socket, address)
        if wait_for_ack(i, client_socket):
            i += 1


def send_block(b_num, block, client_socket, address):
    """
    :author: Elisha Hamp
    Takes in the block number and the block of bits to send,
    and assembles a message to be sent using the info provided.
    :param client_socket: the socket of the client that made the request
    :param address: address received from receiving bytes from the client
    :param b_num:
    :param block:
    :
    """
    code = b'\x00\x03'
    block_num = b_num.to_bytes(2, 'big')
    response = code + block_num + block
    client_socket.sendto(response, address)


def wait_for_ack(b_num, client_socket):
    """
    Takes in the block number of the block which was just sent, then waits
    for the client ack message. It then either times out or receives an ack.
    If it receives an ack, it then compares the ack number to the param number.
    :param b_num: the number of the block which was just sent
    :param client_socket: the socket of the client that made the request
    :return: whether the ack received was positive
    """
    client_socket.settimeout(5)
    positive_ack = False
    try:
        positive_ack = receive_ack(b_num, client_socket)
    except TimeoutError:
        return positive_ack
    return positive_ack


def receive_ack(b_num, client_socket):
    """
    :author: Elisha Hamp
    Receives an acknowledgement packet and uses it to determine whether
    the ack is useful or if a packet needs to be resent.
    :param b_num: the number of the block which was just sent
    :param client_socket: the socket of the client that made the request
    :return: whether the ack received was positive
    """
    positive_ack = False
    ack, address = client_socket.recvfrom(MAX_UDP_PACKET_SIZE)
    code, received_b_num = parse_ack(ack)
    if code == 4 and b_num == b_num:
        positive_ack = True
    return positive_ack


def parse_ack(ack):
    """
    :author: Elisha Hamp
    parses the acknowledgement response.
    :param ack: The acknowledgement bytes received.
    :return: the operation-code and block number received from the acknowledgement.
    """
    code = int.from_bytes(ack[0: 2], 'big')
    b_num = int.from_bytes(ack[2: 4], 'big')

    return code, b_num


main()
