'Functional Tests'

import os, re
from subprocess import Popen, PIPE

#   Global configuration for all functional tests.
os.environ.pop('SSH_AUTH_SOCK', None)
DEVNULL = open(os.devnull, 'rwb')

def test_global_config():
    assert None is os.environ.get('SSH_AUTH_SOCK')

def test_popen_ssh():
    'Demonstrate use of Popen in a test.'
    p = Popen(['ssh', '-n', '-h'], stdin=DEVNULL, stdout=PIPE, stderr=PIPE,
        env={}, bufsize=-1, close_fds=True)
    assert 0 <= p.wait()            # Any retval but not terminated by a signal.
    assert '' == p.stdout.read()    # XXX should close these?
    assert re.search('usage: ssh', p.stderr.read())
