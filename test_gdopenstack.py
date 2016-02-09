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
        assert 'Hello, gbin@localhost' in testbot.pop_message()

    def test_nova_listservers(self, testbot):
        testbot.push_message('!nova listservers')
        response = testbot.pop_message()
        assert "smcquaid-dev1" in response

    def test_nova_getip(self, testbot):
        testbot.push_message('!nova getip smcquaid-dev1')
        response = testbot.pop_message()
        assert "10.224.78.86" in response

        testbot.push_message('!nova getip 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        response = testbot.pop_message()
        assert "10.224.78.86" in response

    def test_nova_getcreator(self, testbot):
        testbot.push_message('!nova getcreator 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        response = testbot.pop_message()
        assert "smcquaid" in response

        testbot.push_message('!nova getcreator smcquaid-dev1')
        response = testbot.pop_message()
        assert "smcquaid" in response

    def test_nova_getmetadata(self, testbot):
        testbot.push_message('!nova getmetadata 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        response = testbot.pop_message()
        assert "smcquaid" in response

        testbot.push_message('!nova getmetadata smcquaid-dev1')
        response = testbot.pop_message()
        assert "smcquaid" in response
        assert "26 - DEV-Private Cloud" in response
        assert "login_groups" in response
        assert "login_users" in response
        assert "owning_group" in response
        assert "smcquaid" in response


    def test_nova_getusers(self, testbot):
        testbot.push_message('!nova getusers 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        response = testbot.pop_message()
        assert "smcquaid" in response
        assert "dbingham" in response
        assert "jerobinson" in response
        assert "su_devcloud" in response
        assert "ac_devcloud" in response

        testbot.push_message('!nova getusers smcquaid-dev1')
        response = testbot.pop_message()
        assert "smcquaid" in response
        assert "dbingham" in response
        assert "jerobinson" in response
        assert "su_devcloud" in response
        assert "ac_devcloud" in response

    def test_keystone_addadmintoproject(self, testbot):
        # Get base state
        testbot.push_message('!keystone listprojectusers dev-smcquaid')
        response = testbot.pop_message()
        assert "dxstarr" not in response

        # Add User
        testbot.push_message('!keystone addadmintoproject dxstarr dev-smcquaid')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response

        # Check state
        testbot.push_message('!keystone listprojectusers dev-smcquaid')
        response = testbot.pop_message()
        assert "dxstarr" in response

        # Clean up
        testbot.push_message('!keystone removeadminfromproject dxstarr dev-smcquaid')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response

        # Check base state
        testbot.push_message('!keystone listprojectusers dev-smcquaid')
        response = testbot.pop_message()
        assert "dxstarr" not in response

    def test_keystone_listprojects(self, testbot):
        testbot.push_message('!keystone listprojects')
        response = testbot.pop_message()
        assert "user-smcquaid" in response

    def test_keystone_listroles(self, testbot):
        testbot.push_message('!keystone listroles')
        response = testbot.pop_message()
        assert "Member" in response
        assert "ProjectAdmin" in response

    def test_keystone_listprojectusers(self, testbot):
        testbot.push_message('!keystone listprojectusers dev-smcquaid')
        response = testbot.pop_message()
        assert "dxstarr" not in response
        assert "smcquaid" in response

    def test_keystone_removeadminfromproject(self, testbot):
        #Included as above
        pass

    def test_keystone_createproject(self, testbot):
        pass

    def test_nova_addadmintoserver(self, testbot):
        # Get base state
        testbot.push_message('!nova getusers smcquaid-dev1')
        response = testbot.pop_message()
        assert "dxstarr" not in response

        # Add User
        testbot.push_message('!nova addadmintoserver dxstarr smcquaid-dev1')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response

        # Check state
        testbot.push_message('!nova getusers smcquaid-dev1')
        response = testbot.pop_message()
        assert "dxstarr" in response

        # Clean up
        testbot.push_message('!nova removeadminfromserver dxstarr smcquaid-dev1')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response

        # Check base state
        testbot.push_message('!nova getusers smcquaid-dev1')
        response = testbot.pop_message()
        assert "dxstarr" not in response

    def test_nova_removeadminfromserver(self, testbot):
        pass

    def test_nove_forcedelete(self, testbot):
        pass
        # testbot.push_message('!nova getip 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        # response = testbot.pop_message()
        # assert "10.224.78.86" in response

        # testbot.push_message('!nova forcedelete 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        # response = testbot.pop_message()
        # assert "Deleting..." in response

        # testbot.push_message('!nova getip 167bf8a4-ea62-4b8c-b31b-92d66a15d8e9')
        # response = testbot.pop_message()
        # assert "10.224.78.86" not in response