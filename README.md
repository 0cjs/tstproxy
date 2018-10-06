TSTproxy - TCP Proxy via SSH Tunnelling
=======================================

This program sets up and returns a TCP connection to a given address
and port; a typical use would be a connection to an SSH server to be
used by an SSH client.

In the trivial case the host is directly reachable and a direct
connection is made. More commonly the host cannot be directly reached
and one or more proxies must be set up. TSTproxy starts SSH clients to
act as the necessary proxies based on its configuration file.
