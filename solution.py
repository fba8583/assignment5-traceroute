

    Home
        Public

Questions
Tags
Users
Companies
Collectives

    Explore Collectives

    Teams
    Stack Overflow for Teams – Start collaborating and sharing organizational knowledge. 

Creating an ICMP traceroute in Python
Asked 10 years ago
Modified 5 years, 3 months ago
Viewed 5k times
0
2

I am trying to implement an ICMP based Traceroute in Python. I found a very helpful guide ( https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your ) that has allowed me to create a UDP based Traceroute so just needs modification. However I have looked around and am having trouble changing the send socket and making it work. Is anybody able to assist me?

 #!/usr/bin/python

import socket

def main(dest_name):
    dest_addr = socket.gethostbyname(dest_name)
    port = 33434
    max_hops = 30
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1
    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv_socket.bind(("", port))
        send_socket.sendto("", (dest_name, port))
        curr_addr = None
        curr_name = None
        try:
            _, curr_addr = recv_socket.recvfrom(512)
            curr_addr = curr_addr[0]
            try:
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.error:
                curr_name = curr_addr
        except socket.error:
            pass
        finally:
            send_socket.close()
            recv_socket.close()

        if curr_addr is not None:
            curr_host = "%s (%s)" % (curr_name, curr_addr)
        else:
            curr_host = "*"
        print "%d\t%s" % (ttl, curr_host)

        ttl += 1
        if curr_addr == dest_addr or ttl &gt; max_hops:
            break

if __name__ == "__main__":
    main('google.com')

