import os
import gdopenstack
import unittest
from errbot import plugin_manager
from errbot.backends.test import testbot
from novaclient.client import Client


class TestGDOpenstack(object):
    extra_plugin_dir = '.'

    def test_nova_listservers(self, testbot):
        testbot.push_message('!nova listservers --project_id f48e57277a7a484290ba9afdc49a21a9')
        response = testbot.pop_message(timeout=30)
        assert "smcquaid-dev" in response

        testbot.push_message('!nova listservers --project_name openstack')
        response = testbot.pop_message(timeout=1)
        assert "smcquaid-dev" in response

        testbot.push_message('!nova listservers')
        response = testbot.pop_message(timeout=1)
        assert "Too few arguments given" in response


    def test_nova_getip(self, testbot):
        testbot.push_message('!nova getip --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=2)
        assert "10.224.78.218" in response

        testbot.push_message('!nova getip --server_id d1264da8-b428-47f4-aefa-4d263236f403')
        response = testbot.pop_message(timeout=2)
        assert "10.224.78.218" in response


    def test_nova_getmetadata(self, testbot):
        testbot.push_message('!nova getmetadata --server_id d1264da8-b428-47f4-aefa-4d263236f403')
        response = testbot.pop_message(timeout=2)
        assert "smcquaid" in response

        testbot.push_message('!nova getmetadata --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=2)
        assert "smcquaid" in response
        assert "26 - DEV-Private Cloud" in response
        assert "login_groups" in response
        assert "login_users" in response
        assert "owning_group" in response
        assert "smcquaid" in response


    def test_nova_getcreator(self, testbot):
        testbot.push_message('!nova getcreator --server_id d1264da8-b428-47f4-aefa-4d263236f403')
        response = testbot.pop_message(timeout=2)
        assert "smcquaid" in response

        testbot.push_message('!nova getcreator --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=2)
        assert "smcquaid" in response


    def test_nova_getusers(self, testbot):
        testbot.push_message('!nova getusers --server_id d1264da8-b428-47f4-aefa-4d263236f403')
        response = testbot.pop_message(timeout=2)
        assert "smcquaid" in response
        assert "dbingham" in response
        assert "jerobinson" in response
        assert "su_devcloud" in response
        assert "ac_devcloud" in response

        testbot.push_message('!nova getusers --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=2)
        assert "smcquaid" in response
        assert "dbingham" in response
        assert "jerobinson" in response
        assert "su_devcloud" in response
        assert "ac_devcloud" in response

    def test_keystone_listprojectusers(self, testbot):
        testbot.push_message('!keystone listprojectusers --project_name dev-smcquaid')
        response = testbot.pop_message(timeout=2)
        assert "dxstarr" not in response
        assert "smcquaid" in response

        # @TODO need to add test for listprojectusers by id
        testbot.push_message('!keystone listprojectusers --project_id 2e1d7ae656eb406891488643cd4ef922')
        response = testbot.pop_message(timeout=10)
        assert "dxstarr" not in response
        assert "smcquaid" in response

    def test_keystone_addadmintoproject(self, testbot):
        # Get base state
        testbot.push_message('!keystone listprojectusers --project_name dev-smcquaid')
        response = testbot.pop_message()
        assert "dxstarr" not in response

        # Add User
        testbot.push_message('!keystone addadmintoproject --user_name dxstarr --project_name dev-smcquaid')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response
        # @TODO - need to use project ID for code coverage

        # Check state
        testbot.push_message('!keystone listprojectusers --project_name dev-smcquaid')
        response = testbot.pop_message(timeout=10)
        assert "dxstarr" in response

        # Clean up
        testbot.push_message('!keystone removeadminfromproject --user_name dxstarr --project_name dev-smcquaid')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response

        # Check base state
        testbot.push_message('!keystone listprojectusers --project_name dev-smcquaid')
        response = testbot.pop_message(timeout=10)
        assert "dxstarr" not in response

    def test_keystone_removeadminfromproject(self, testbot):
        #Included as above
        pass

    def test_keystone_listprojects(self, testbot):
        testbot.push_message('!keystone listprojects')
        response = testbot.pop_message(timeout=10)
        assert "user-smcquaid" in response

    def test_keystone_listroles(self, testbot):
        testbot.push_message('!keystone listroles')
        response = testbot.pop_message(timeout=10)
        assert "Member" in response
        assert "ProjectAdmin" in response

    def test_nova_addadmintoserver(self, testbot):
        # Get base state
        testbot.push_message('!nova getusers --server_name smcquaid-dev2')
        response = testbot.pop_message()
        assert "dxstarr" not in response

        # Add User
        testbot.push_message('!nova addadmintoserver --user_name dxstarr --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response

        # Check state
        testbot.push_message('!nova getusers --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=10)
        assert "dxstarr" in response

        # Clean up
        testbot.push_message('!nova removeadminfromserver --user_name dxstarr --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=10)
        assert "Success" in response

        # Check base state
        testbot.push_message('!nova getusers --server_name smcquaid-dev2')
        response = testbot.pop_message(timeout=10)
        assert "dxstarr" not in response

    def test_nova_removeadminfromserver(self):
        pass

    def test_nova_forcedelete(self):
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

    def test_keystone_createproject(self):
        pass

    def test_ad_clearhostname(self):
        pass
