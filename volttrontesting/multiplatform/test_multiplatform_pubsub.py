import os

import gevent
import pytest
import json
from volttrontesting.utils.utils import (poll_gevent_sleep,
                                         messages_contains_prefix)

from volttrontesting.fixtures.volttron_platform_fixtures import get_rand_vip, \
    build_wrapper, get_rand_ip_and_port
from volttrontesting.utils.platformwrapper import PlatformWrapper
from volttron.platform.agent.known_identities import PLATFORM_DRIVER, CONFIGURATION_STORE

subscription_results = {}
def onmessage(peer, sender, bus, topic, headers, message):
    global subscription_results
    subscription_results[topic] = {'headers': headers, 'message': message}
    print("xxxsubscription_results[{}] = {}".format(topic, subscription_results[topic]))

@pytest.fixture(scope="module")
def get_volttron_instances(request):
    """ Fixture to get more than 1 volttron instance for test
    Use this fixture to get more than 1 volttron instance for test. This
    returns a function object that should be called with number of instances
    as parameter to get a list of volttron instnaces. The fixture also
    takes care of shutting down all the instances at the end

    Example Usage:

    def test_function_that_uses_n_instances(get_volttron_instances):
        instance1, instance2, instance3 = get_volttron_instances(3)

    @param request: pytest request object
    @return: function that can used to get any number of
        volttron instances for testing.
    """
    all_instances = []

    def get_n_volttron_instances(n, should_start=True, address_file=True):
        get_n_volttron_instances.count = n
        instances = []
        vip_addresses = []
        web_addresses = []
        instances = []
        addr_config = dict()

        # vip_addresses.append('tcp://127.0.0.18:22916')
        # vip_addresses.append('tcp://127.0.0.16:22916')
        # web_addresses.append('http://127.0.0.18:8080')
        # web_addresses.append('http://127.0.0.16:8080')
        for i in range(0, n):
            address = get_rand_vip()
            web_address = "http://{}".format(get_rand_ip_and_port())
            vip_addresses.append(address)
            web_addresses.append(web_address)
            nm = 'platform' + str(i+1)
            addr_config[nm] = {"instance-name": nm, "vip-address": address, "bind-web-address": web_address}

        #
        # addr_config['platform1'] = {"instance-name": "platform1", "vip-address": vip_addresses[0], "bind-web-address": web_addresses[0]}
        # addr_config['platform2'] = {"instance-name": "platform2", "vip-address": vip_addresses[1], "bind-web-address": web_addresses[1]}
        for i in range(0, n):
            address = vip_addresses.pop(0)
            web_address = web_addresses.pop(0)
            print address, web_address
            wrapper = None
            wrapper = PlatformWrapper()
            instances.append(wrapper)

            addr_file = os.path.join(wrapper.volttron_home, 'external_address.json')
            print addr_config
            if address_file:
                with open(addr_file, 'w') as f:
                    json.dump(addr_config, f)
                    gevent.sleep(.1)
            wrapper.startup_platform(address, bind_web_address=web_address)
            wrapper.allow_all_connections()
        instances = instances if n > 1 else instances[0]
        # setattr(get_n_volttron_instances, 'instances', instances)
        get_n_volttron_instances.instances = instances
        return instances
    #
    # def cleanup():
    #     if isinstance(get_n_volttron_instances.instances, PlatformWrapper):
    #         print('Shutting down instance: {}'.format(
    #             get_n_volttron_instances.instances.volttron_home))
    #         get_n_volttron_instances.instances.shutdown_platform()
    #         return
    #
    #     for i in range(0, get_n_volttron_instances.count):
    #         print('Shutting down instance: {}'.format(
    #             get_n_volttron_instances.instances[i].volttron_home))
    #         get_n_volttron_instances.instances[i].shutdown_platform()
    #
    # request.addfinalizer(cleanup)

    return get_n_volttron_instances


@pytest.fixture(scope="module")
def multi_platform_connection(request, get_volttron_instances):
    """
    Adds the volttron-central-address and volttron-central-serverkey to the
    main instance configuration file before starting the platform
    """
    p1, p2, p3 = get_volttron_instances(3)

    gevent.sleep(5)

    # configure vc
    agent1 = p1.build_agent()
    agent2 = p2.build_agent()
    agent3 = p3.build_agent()

    def stop():
        agent1.core.stop()
        agent2.core.stop()
        agent3.core.stop()
        p1.shutdown_platform()
        p2.shutdown_platform()
        p3.shutdown_platform()

    request.addfinalizer(stop)

    return agent1, agent2, agent3

@pytest.fixture(scope="module")
def five_platform_connection(request, get_volttron_instances):
    """
    Adds the volttron-central-address and volttron-central-serverkey to the
    main instance configuration file before starting the platform
    """
    p1, p2, p3, p4, p5 = get_volttron_instances(5)

    gevent.sleep(5)

    # configure vc
    agent1 = p1.build_agent()
    agent2 = p2.build_agent()
    agent3 = p3.build_agent()
    agent4 = p4.build_agent()
    agent5 = p5.build_agent()

    def stop():
        agent1.core.stop()
        agent2.core.stop()
        agent3.core.stop()
        agent4.core.stop()
        agent5.core.stop()
        p1.shutdown_platform()
        p2.shutdown_platform()
        p3.shutdown_platform()
        p4.shutdown_platform()
        p5.shutdown_platform()

    request.addfinalizer(stop)

    return agent1, agent2, agent3, agent4, agent5

def test_multiplatform_pubsub(request, multi_platform_connection):
    p1_publisher, p2_listener, p3_listener = multi_platform_connection

    def callback2(peer, sender, bus, topicdr, headers, message):
        print message
        assert message == [{'point':'vac,;v;lue'}]
    def callback3(peer, sender, bus, topic, headers, message):
        print message

    def callback4(peer, sender, bus, topic, headers, message):
        print message
    def callback5(peer, sender, bus, topic, headers, message):
        print message

    p2_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=onmessage,
                               all_platforms=True)
    gevent.sleep(2)
    p3_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=onmessage)
    print "publish"
    prefix= 'devices'
    for i in range(10):
        p1_publisher.vip.pubsub.publish(peer='pubsub', topic='devices/campus/building1', message=[{'point':'value'}])
        #gevent.sleep(0.1)

        poll_gevent_sleep(2, lambda: messages_contains_prefix(prefix,
                                                              subscription_results))

        message = subscription_results['devices/campus/building1']['message']
        assert message == [{'point':'value'}]
    gevent.sleep(5)

def test_multiplatform_2_publishers(request, five_platform_connection):
    subscription_results2 = {}
    subscription_results3 = {}
    subscription_results4 = {}
    subscription_results5 = {}

    p1_publisher, p2_listener, p3_listener, p4_listener, p5_publisher = five_platform_connection

    def callback2(peer, sender, bus, topic, headers, message):
        subscription_results2[topic] = {'headers': headers, 'message': message}
        print("platform2 sub results [{}] = {}".format(topic, subscription_results2[topic]))

    def callback3(peer, sender, bus, topic, headers, message):
        subscription_results3[topic] = {'headers': headers, 'message': message}
        print("platform3 sub results [{}] = {}".format(topic, subscription_results3[topic]))

    def callback4(peer, sender, bus, topic, headers, message):
        subscription_results4[topic] = {'headers': headers, 'message': message}
        print("platform4 sub results [{}] = {}".format(topic, subscription_results4[topic]))

    def callback5(peer, sender, bus, topic, headers, message):
        subscription_results5[topic] = {'headers': headers, 'message': message}
        print("platform4 sub results [{}] = {}".format(topic, subscription_results5[topic]))

    p2_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=callback2,
                               all_platforms=True)

    p3_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=callback3,
                               all_platforms=True)
    gevent.sleep(2)
    p4_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='analysis',
                               callback=callback4,
                               all_platforms=True)

    p5_publisher.vip.pubsub.subscribe(peer='pubsub',
                               prefix='analysis',
                               callback=callback5)
    gevent.sleep(2)
    print "publish"
    prefix= 'devices'
    for i in range(5):
        p1_publisher.vip.pubsub.publish(peer='pubsub', topic='devices/campus/building1', message=[{'point':'value'}])
        poll_gevent_sleep(1, lambda: messages_contains_prefix(prefix,
                                                              subscription_results2))
        message = subscription_results2['devices/campus/building1']['message']
        assert message == [{'point':'value'}]
        message = subscription_results3['devices/campus/building1']['message']
        assert message == [{'result': 'value'}]

    prefix = 'analysis'
    for i in range(5):
        p5_publisher.vip.pubsub.publish(peer='pubsub', topic='analysis/airside/campus/building1', message=[{'result':'pass'}])
        #gevent.sleep(0.1)

        poll_gevent_sleep(2, lambda: messages_contains_prefix(prefix,
                                                              subscription_results3))
        message = subscription_results4['analysis/airside/campus/building1']['message']
        assert message == [{'result':'pass'}]
        message = subscription_results5['analysis/airside/campus/building1']['message']
        assert message == [{'result':'pass'}]



def test_multiplatform_subscribe_unsubscribe(request, multi_platform_connection):
    subscription_results2 = {}
    subscription_results3 = {}
    message_count = 0
    p1_publisher, p2_listener, p3_listener = multi_platform_connection

    def callback2(peer, sender, bus, topic, headers, message):
        subscription_results2[topic] = {'headers': headers, 'message': message}
        print("platform2 sub results [{}] = {}".format(topic, subscription_results2[topic]))

    def callback3(peer, sender, bus, topic, headers, message):
        subscription_results3[topic] = {'headers': headers, 'message': message}
        print("platform3 sub results [{}] = {}".format(topic, subscription_results3[topic]))

    p2_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=callback2,
                               all_platforms=True)

    p3_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=callback3,
                               all_platforms=True)
    gevent.sleep(2)

    prefix= 'devices'
    i=0
    for i in range(2):
        p1_publisher.vip.pubsub.publish(peer='pubsub', topic='devices/campus/building1', message=[{'point':'value'+str(i)}])
        gevent.sleep(0.3)
        message = subscription_results2['devices/campus/building1']['message']
        assert message == [{'point':'value'+str(i)}]
        message = subscription_results3['devices/campus/building1']['message']
        assert message == [{'point': 'value'+str(i)}]
        print "pass"

    #Listener agent on platform 2 unsubscribes frm prefix='devices'
    p2_listener.vip.pubsub.unsubscribe(peer='pubsub', prefix='devices', callback=callback2, all_platforms=True)
    gevent.sleep(0.2)

    p1_publisher.vip.pubsub.publish(peer='pubsub', topic='devices/campus/building1', message=[{'point': 'value'+str(2)}])
    gevent.sleep(0.4)
    message = subscription_results2['devices/campus/building1']['message']
    assert message == [{'point':'value1'}]
    gevent.sleep(0.4)
    message = subscription_results3['devices/campus/building1']['message']
    assert message == [{'point': 'value2'}]

def test_multiplatform_stop_subscriber(request, multi_platform_connection):
    subscription_results2 = {}
    subscription_results3 = {}
    message_count = 0
    p1_publisher, p2_listener, p3_listener = multi_platform_connection

    def callback2(peer, sender, bus, topic, headers, message):
        subscription_results2[topic] = {'headers': headers, 'message': message}
        print("platform2 sub results [{}] = {}".format(topic, subscription_results2[topic]))

    def callback3(peer, sender, bus, topic, headers, message):
        subscription_results3[topic] = {'headers': headers, 'message': message}
        print("platform3 sub results [{}] = {}".format(topic, subscription_results3[topic]))

    p2_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=callback2,
                               all_platforms=True)

    p3_listener.vip.pubsub.subscribe(peer='pubsub',
                               prefix='devices',
                               callback=callback3,
                               all_platforms=True)
    gevent.sleep(2)

    prefix= 'devices'
    i=0
    for i in range(2):
        p1_publisher.vip.pubsub.publish(peer='pubsub', topic='devices/campus/building1', message=[{'point':'value'+str(i)}])
        gevent.sleep(0.3)
        message = subscription_results2['devices/campus/building1']['message']
        assert message == [{'point':'value'+str(i)}]
        message = subscription_results3['devices/campus/building1']['message']
        assert message == [{'point': 'value'+str(i)}]
        print "pass"

    #Stop listener agent on platform 2
    p2_listener.core.stop()
    gevent.sleep(0.2)

    p1_publisher.vip.pubsub.publish(peer='pubsub', topic='devices/campus/building1', message=[{'point': 'value'+str(2)}])
    gevent.sleep(0.4)
    message = subscription_results2['devices/campus/building1']['message']
    assert message == [{'point':'value1'}]
    gevent.sleep(0.4)
    message = subscription_results3['devices/campus/building1']['message']
    assert message == [{'point': 'value2'}]

def test_missing_address_file(request, get_volttron_instances):
    p1 = get_volttron_instances(1, address_file=False)
    gevent.sleep(1)
    p1.shutdown_platform()

def test_multiplatform_rpc(request, get_volttron_instances):
    p1, p2 = get_volttron_instances(2)
    _default_config = {
        "test_max": {
            "threshold_max": 10
        }
    }
    threshold_detection_uuid = p1.install_agent(
        agent_dir='services/core/ThresholdDetectionAgent',
        config_file=_default_config,
        start=True)

    updated_config = {
        "updated_topic": {
            "threshold_max": 10,
            "threshold_min": 2,
        }
    }
    test_agent = p2.build_agent()
    test_agent.vip.rpc.call(CONFIGURATION_STORE,
                    'manage_store',
                    'platform.thresholddetection',
                    'config',
                    json.dumps(updated_config),
                    'json',
                    platform='platform1').get(timeout=10)
    config = test_agent.vip.rpc.call(CONFIGURATION_STORE,
                    'manage_get',
                    'platform.thresholddetection',
                    'config',
                    raw=True,
                    platform='platform1').get(timeout=10)
    config = json.loads(config)
    try:
        assert config == updated_config
    except KeyError:
        pytest.fail("Expecting config change : {}".format(config))

    def stop():
        p1.stop_agent(threshold_detection_uuid)
        p2.remove_agent(threshold_detection_uuid)
        p1.shutdown_platform()
        test_agent.core.stop()
        p1.shutdown_platform()

    request.addfinalizer(stop)




