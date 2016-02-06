import os
import gdopenstack
import unittest
from errbot import plugin_manager
from errbot.backends.test import testbot
from novaclient.client import Client



class TestGDOpenstack(object):
    extra_plugin_dir = '.'

    def test_hello(self, testbot):
        testbot.push_message('!hello')
        # testbot.log.info(response)
        assert 'Hello, gbin@localhost' in testbot.pop_message()

    def test_listservers(self, testbot):
        testbot.push_message('!nova listservers')
        response = str(testbot.pop_message())
        # testbot.log.info(response)
        assert "smcquaid-dev1" in response

    def test_getip(self, testbot):
        testbot.push_message('!nova getip smcquaid-dev1')
        response = testbot.pop_message()
        # testbot.log.info(response)
        assert "10.224.78.86" in response

        testbot.push_message('!nova getip 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        response = testbot.pop_message()
        # testbot.log.info(response)
        assert "10.224.78.86" in response

    def test_getcreator(self, testbot):
        testbot.push_message('!nova getcreator 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        response = testbot.pop_message()
        # testbot.log.info(response)
        assert "smcquaid" in response

        testbot.push_message('!nova getcreator smcquaid-dev1')
        response = testbot.pop_message()
        # testbot.log.info(response)
        assert "smcquaid" in response

    def test_getmetadata(self, testbot):
        pass
        # testbot.push_message('!nova getmetadata smcquaid-dev1')
        # response = testbot.pop_message()
        # assert "10.224.78.86" in response

    def test_getowners(self, testbot):
        pass
        # testbot.push_message('!nova getcreator smcquaid-dev1')
        # response = testbot.pop_message()
        # assert "smcquaid" in response

    def test_getusers(self, testbot):
        pass
        # testbot.push_message('!getusers smcquaid-dev1')
        # response = testbot.pop_message()
        # assert "smcquaid" in response
        # NEED to add another user here






# def get_nova_credentials_v2():
#     d = {}
#     d['version'] = '2'
#     d['username'] = os.environ['OS_USERNAME']
#     d['api_key'] = os.environ['OS_PASSWORD']
#     d['auth_url'] = os.environ['OS_AUTH_URL']
#     d['project_id'] = os.environ['OS_TENANT_NAME']
#     return d

# credentials = get_nova_credentials_v2()
# nova_client = Client(**credentials)
# print(nova_client.servers.list())
# print(nova_client.fixed_ips.list())