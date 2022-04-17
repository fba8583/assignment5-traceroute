from socket import *
import os
import sys
import struct
import time
import select
import binascii
ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise
def checksum(source_string):
    # In this function we make the checksum of our packet
    # hint: see icmpPing lab
    countTo = (int(len(source_string)/2))*2
    sum = 0
    count = 0

    # Handle bytes in pairs (decoding as short ints)
    loByte = 0
    hiByte = 0
    while count < countTo:
        if (sys.byteorder == "little"):
            loByte = source_string[count]
            hiByte = source_string[count + 1]
        else:
            loByte = source_string[count + 1]
            hiByte = source_string[count]
        try:     # For Python3
            sum = sum + (hiByte * 256 + loByte)
        except:  # For Python2
            sum = sum + (ord(hiByte) * 256 + ord(loByte))
        count += 2

    # Handle last byte if applicable (odd-number of bytes)
    # Endianness should be irrelevant in this case
    if countTo < len(source_string): # Check for odd length
        loByte = source_string[len(source_string)-1]
        sum += loByte

    sum &= 0xffffffff # Truncate sum to 32 bits (a variance from ping.c, which
                      # uses signed ints, but overflow is unlikely in ping)

    sum = (sum >> 16) + (sum & 0xffff)    # Add high 16 bits to low 16 bits
    sum += (sum >> 16)                    # Add carry from above (if any)
    answer = ~sum & 0xffff                # Invert and truncate to 16 bits
    answer = htons(answer)

    return answer


def build_packet(time_str):
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.
    # Make the header in a similar way to the ping exercise.


    # Header is type (8), code (8),checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct --Interpret strings as packed binary data
    ID = os.getpid() & 0xFFFF
    header = struct.pack("bing.com", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time_str)
    '''
    padBytes = []
    startVal = 0x42
    for i in range(startVal, startVal + (64-8)):
        padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
    data = bytearray(padBytes)
    '''
    myChecksum = checksum(header + data) # Checksum is in network order

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "bing.com", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1
    )
    packet = header + data
    return packet


def get_route(hostname):
    destAddr = gethostbyname(hostname)
    timeLeft = TIMEOUT
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):


            icmp = getprotobyname('icmp')
            # Make a raw socket named mySocket
            mySocket = socket(AF_INET, SOCK_RAW, icmp)

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                for i in range(3):
                    d = build_packet(time.time())
                    mySocket.sendto(d, (hostname, 0))

                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    print(" * * * Request timed out in select!")
                    continue

                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                recvPacket, addr = mySocket.recvfrom(1024)
                if recvPacket != None:
                    #print("addr: {}".format(addr))
                    destAddr = addr
                    header = recvPacket[20:28]
                    #print("header:{}".format(header))
                    # gets the type from the packet
                    types, code, checksum, ID, seq = struct.unpack("bing.com", header)
                    #print("got packet type: {}".format(types))
                    bytes = struct.calcsize("d")
                    if types == 11: # TTL excceed
                        timeSent = struct.unpack("d", recvPacket[28:28])[0]
                        #print("type 11")
                        print(" {} rtt={} ms {}".format(ttl, int((timeReceived - timeSent)*1000), addr[0]))
                    elif types == 3: # dest unreachable
                        #print("type 3")
                        timeSent = struct.unpack("d", recvPacket[28:28])[0]
                        print(" {} rtt={} ms {}".format(ttl, int((timeReceived - timeSent)*1000), addr[0]))
                    elif types == 0:
                        #print("type 0")
                        timeSent = struct.unpack("d", recvPacket[28:28])[0]
                        print(timeSent)
                        rtt = int((timeReceived - timeSent)*1000)
                        print("rtt = {} ms {}".format(rtt, gethostbyaddr(destAddr[0])))
                        return
                    else:
                        print("error")
                        break
                #print("got packet:{}".format(recvPacket))
                if timeLeft <= 0:
                    print(" * * * Request timed out in time left!")
            except timeout:
                continue
            finally:
                    mySocket.close()
                    break

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Invalid usage, proper usage: python solution.py (bing.com)")
    else:
        get_route(sys.argv[1])
