'Functional Tests'

import os, re, pytest
from random import randrange
from subprocess import Popen, PIPE
from twisted.internet import protocol

####################################################################
#   Framework for testing with Twisted

@pytest.fixture
def reactor():
    timeout_secs = 3
    #   We want a reactor that works on all platforms.
    from twisted.internet.selectreactor import SelectReactor
    r = SelectReactor()
    d = { 'forced': False }     # No `nonlocal` in Python 2
    def force_stop():
        d['forced'] = True
        r.stop()
    r.callLater(timeout_secs, force_stop)
    yield r
    if d['forced']: pytest.fail(
        'Test did not stop reactor within {} secs'.format(timeout_secs))

def test_reactor_fixture(reactor):
    #   Comment out the next line to see "test did not stop reactor."
    reactor.callWhenRunning(reactor.stop)
    reactor.run()

####################################################################
#   Functional Tests

#   Global configuration for all functional tests.
os.environ.pop('SSH_AUTH_SOCK', None)
DEVNULL = open(os.devnull, 'r+b')

def test_global_config():
    assert None is os.environ.get('SSH_AUTH_SOCK')

def test_tstproxy_help():
    p = Popen(['bin/tstproxy', '-h'], stdin=DEVNULL, stdout=PIPE, stderr=PIPE,
        env={}, bufsize=-1, close_fds=True)
    assert 0 == p.wait()
    assert b'' == p.stderr.read()    # XXX should close these?
    out = p.stdout.read()
    assert re.search(b'usage: tstproxy', out), 'Unexpected stdout:\n' + out

@pytest.mark.skip(reason='Slow test')
def test_twisted_ssh_gpo(reactor):
    ''' getProcessOutput() and the like are convenient, but don't give
        us the ability to run code on process exit as we can with the
        full interface. Thus we have to hack a timeout on the reactor
        making the test slower than necessary.
    '''
    from twisted.internet.utils import getProcessOutputAndValue
    deferred = getProcessOutputAndValue('ssh', ['-h'], reactor=reactor)
    reactor.callLater(0.2, reactor.stop)
    reactor.run()
    out, err, exitcode = deferred.result
    assert '' == out
    assert re.search('usage: ssh', err)
    assert 0 < exitcode

class SSHClientProto(protocol.ProcessProtocol):
    def __init__(self, reactor, received):
        self.reactor, self.received = reactor, received
    def connectionMade(self):
        self.transport.closeStdin()     # Send no input
    def childDataReceived(self, fd, data):
        s = self.received.setdefault(fd, b'')
        self.received[fd] = s + data
    def processEnded(self, reason):
        self.reactor.stop()

def test_twisted_ssh(reactor):
    '   Demonstrate launch of OpenSSH client via twisted   '
    received = {}
    proto = SSHClientProto(reactor, received)
    reactor.spawnProcess(proto, 'ssh', ['ssh', '-h'])   # Empty environment
    reactor.run()
    assert re.search(b'usage: ssh', received[2])
    assert [2] == list(received.keys())     # Nothing but stderr

class SSHTestServerProto(protocol.Protocol):
    def connectionMade(self):
        #   Perhaps we ought to try a bit more of the proto, e.g.,
        #      write('SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u4')
        #   or even use conch. But for now, just close.
        self.transport.loseConnection()

port = randrange(10000, 65000)

def test_ssh_and_server(reactor):
    '   OpenSSH client connects to our test server.   '
    factory = protocol.Factory.forProtocol(SSHTestServerProto)
    reactor.listenTCP(port, factory, interface='127.0.0.1')

    creceived = {}
    cproto = SSHClientProto(reactor, creceived)
    reactor.spawnProcess(cproto,
        'ssh', ['ssh', '-T', '-p', str(port), '127.0.0.1'])

    reactor.run()
    assert b'ssh_exchange_identification: Connection closed by remote host\r\n'\
        == creceived[2]
    assert [2] == list(creceived.keys())

def test_ssh_via_tstproxy(reactor):
    '   OpenSSH client connects to test server via testproxy-passed FD.   '
    factory = protocol.Factory.forProtocol(SSHTestServerProto)
    reactor.listenTCP(port, factory, interface='127.0.0.1')

    creceived = {}
    cproto = SSHClientProto(reactor, creceived)
    reactor.spawnProcess(cproto, 'ssh', ['ssh',
        '-o', 'ProxyCommand=bin/tstproxy --direct 127.0.0.1 %d' % port,
        '-o', 'ProxyUseFdpass=yes',
        '-T', '-p', str(port), '127.0.0.1'])
    reactor.run()

    # XXX need to check that factory received a connection
    assert b'ssh_exchange_identification: Connection closed by remote host\r\n'\
        == creceived[2]
    assert [2] == list(creceived.keys())
