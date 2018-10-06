To-do
=====

* [sshuttle] is single-hop and serves a different purpose, but also
  deals with forwarding network connections via SSH. Have a look at it
  to see if we can steal any ideas related to:
  - Use of `ssh`
  - General handling of network protocols
  - Testing network stuff
  - Using Tox to test under Python 2.7 and 3.5

[sshuttle]: https://github.com/sshuttle/sshuttle.git

* [Paramiko] and [Twisted Conch] are both Python SSHv2
  implementations. Is there anything we're doing that might be better
  done with one of these rather than calling out to OpenSSH?
  Possibilities include running the remote commands to set up proxies
  further down the chain (examples at [conch_client] and [so-4617507])
  and having 'real' SSH in the test framework (server example at
  [g-loaded]), should we ever need it.

[Paramiko]: http://www.paramiko.org/
[Twisted Conch]: https://twistedmatrix.com/trac/wiki/TwistedConch
[conch_client]: https://twistedmatrix.com/documents/16.5.0/conch/howto/conch_client.html
[g-loaded]: https://www.g-loaded.eu/2010/03/26/python-ssh-server-unix-twisted-conch/
[so-4617507]: https://stackoverflow.com/q/4617507
