"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 051
- Fall 2021
- Lab 07
- Names:
  - Elisha Hamp
  - Josiah Clausen

A Trivial File Transfer Protocol Server

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""

# import modules -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket
import os
import math

# Helpful constants used by TFTP
TFTP_PORT = 69
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65536


def main():
    """
    Processes a single TFTP request
    """

    client_socket = socket_setup()

    print("Server is ready to receive a request")

    ####################################################
    # Your code starts here                            #
    #   Be sure to design and implement additional     #
    #   functions as needed                            #
    ####################################################

    print(parse_request(receive_request(client_socket)))

    ################################################JOSIAH ^ ELI



    ####################################################
    # Your code ends here                              #
    ####################################################

    client_socket.close()


def get_file_block_count(filename):
    """
    Determines the number of TFTP blocks for the given file
    :param filename: THe name of the file
    :return: The number of TFTP blocks for the file or -1 if the file does not exist
    """
    try:
        # Use the OS call to get the file size
        #   This function throws an exception if the file doesn't exist
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
    block_byte_offset = (block_number-1) * TFTP_BLOCK_SIZE
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
    block_byte_offset = (block_number-1) * TFTP_BLOCK_SIZE
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


####################################################
# Write additional helper functions starting here  #
####################################################
def receive_request(receive_request):
    byte = receive_request.recv(1024)
    print(str(byte)+"THIS IS THE BYTES RECIEVED")
    return byte
    pass


def parse_request(request):
    """
    Gets the request and determines what to do with it
    :param request:
    :return:
    """
    type = request[0: 2]
    print(str(type)+"THIS IS THE FIRST BYTE")
    op_code = 5
    file_name = b''
    mode = b''
    if type == b'\x00\x01':
        op_code = 1
        code = request.replace(b'\x00\01', b'')
        print("GETFILE HAS BEEN CHOSEN")
        file_name = code[0: code.index(b'\x00')]
        print(file_name)
        code = code.replace(file_name+b'\x00', b'')
        mode = code[0: code.index(b'\x00')]
        print(mode)

    return op_code, file_name, mode
    pass

def verify_request():
    pass

def send_error():
    pass

############################################### JOSIAH

def read_file(file_name):
    """
    :author: Elisha Hamp
    Takes in a file_name and uses it to create blocks
    :param file_name:
    :return:
    """
    pass


def send_block(number, block):
    """
    :author: Elisha Hamp
    Takes in the block number and the block of bits to send,
    and assembles a message to be sent using the info provided.
    :param number:
    :param block:
    :return:
    """
    pass


def wait_for_ack(number):
    """
    Takes in the block number of the block which was just sent, then waits
    for the client ack message. It then either times out or receives an ack.
    If it receives an ack, it then compares the ack number to the param number.
    :param number:
    :return:
    """
    pass


def parse_ack(ack):
    """
    :author: Elisha Hamp
    parses the ack
    :param ack:
    :return:
    """
    pass


main()
