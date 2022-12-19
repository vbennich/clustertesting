import pytest
import signal
@pytest.fixture(scope='session', autouse=True)
def term_handler():
    orig = signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))
    yield
    signal.signal(signal.SIGTERM, orig)