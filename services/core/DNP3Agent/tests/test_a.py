import gevent
import pytest
import time

from volttrontesting.utils.platformwrapper import start_wrapper_platform, PlatformWrapper


@pytest.fixture(scope="module")
def setup_instances():

    inst1 = PlatformWrapper()
    inst2 = PlatformWrapper()

    start_wrapper_platform(inst1)
    start_wrapper_platform(inst2)

    yield inst1, inst2

    inst1.shutdown_platform()
    inst2.shutdown_platform()


@pytest.mark.wrapper
def test_can_install_listener(volttron_instance):
    clear_messages()
    vi = volttron_instance
    assert vi is not None
    assert vi.is_running()

    auuid = vi.install_agent(agent_dir='/Users/anhnguyen/repos/kisensum-volttron/volttron/services/core/DNP3Agent/tests/ControlAgent',
                             start=False)
    assert auuid is not None
    started = vi.start_agent(auuid)
    print('STARTED: ', started)
    listening = vi.build_agent()
    listening.vip.pubsub.subscribe(peer='pubsub',
                                   prefix='heartbeat/controlagent',
                                   callback=onmessage)
    # sleep for 10 seconds and at least one heartbeat should have been
    # published
    # because it's set to 5 seconds.
    time_start = time.time()

    print('Awaiting heartbeat response.')
    while not messages_contains_prefix(
            'heartbeat/controlagent') and time.time() < time_start + 10:
        gevent.sleep(0.2)

    assert messages_contains_prefix('heartbeat/controlagent')

    stopped = vi.stop_agent(auuid)
    print('STOPPED: ', stopped)
    removed = vi.remove_agent(auuid)
    print('REMOVED: ', removed)


messages = {}


def onmessage(peer, sender, bus, topic, headers, message):
    messages[topic] = {'headers': headers, 'message': message}


def clear_messages():
    global messages
    messages = {}


def messages_contains_prefix(prefix):
    global messages
    return any(map(lambda x: x.startswith(prefix), messages.keys()))


@pytest.mark.wrapper
def test_can_publish(volttron_instance):
    global messages
    clear_messages()
    vi = volttron_instance
    agent = vi.build_agent()
    #    gevent.sleep(0)
    agent.vip.pubsub.subscribe(peer='pubsub', prefix='test/world',
                               callback=onmessage).get(timeout=5)

    agent_publisher = vi.build_agent()
    #    gevent.sleep(0)
    agent_publisher.vip.pubsub.publish(peer='pubsub', topic='test/world',
                                       message='got data')
    # sleep so that the message bus can actually do some work before we
    # eveluate the global messages.
    gevent.sleep(0.1)
    assert messages['test/world']['message'] == 'got data'
