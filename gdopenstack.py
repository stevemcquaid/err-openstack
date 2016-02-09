from errbot import BotPlugin, botcmd
from novaclient.client import Client as nclient
from keystoneclient.v2_0.client import Client as ksclient
import os
import re
import argparse
import json


class GDOpenstack(BotPlugin):
    def activate(self):
        self.novaclient = None
        self.serverlist = None
        self.tenantlist = None

        if self._refreshcache():
            super(GDOpenstack, self).activate()
        else:
            self.log.error("Cache failed to load. Unable to load novaclient.")

    @botcmd(split_args_with=None)
    def refreshcache(self, msg, args):
        return self._refreshcache()

    def _refreshcache(self):
        # @TODO: Can send message that cache is refreshing if desired
        self.novaclient = self._get_nova_client()
        self.keystoneclient = self._get_keystone_client();
        # Get a list of running servers.
        self.serverlist = \
            self.novaclient.servers.list(
                search_opts=dict(all_tenants=True))

        self.tenantlist = self.keystoneclient.tenants.list()

        # @TODO: Can send callback if desired
        # DEBUG: Cache refreshed
        return True

    @botcmd(split_args_with=None)
    def hello(self, msg, args):
        """Say hello to someone"""
        return "Hello, " + format(msg.frm)

    # Helpers

    def _parse_args(self):
        pass

    def _format_network(self, server):
        networks = server.networks.items()
        return networks

    def _find_server_by_id(self, id):
        for server in self.serverlist:
            if id == str(server.id):
                return server
        # Server not found
        return False

    def _find_server_by_name(self, name):
        found = []
        for server in self.serverlist:
            if name == server.name:
                found.append(server)

        return found

    def _get_nova_client(self):
        """ This converts env vars to local vasr & auths with OS """
        credentials = {}
        credentials['version'] = '2'
        credentials['username'] = os.environ['OS_USERNAME']
        credentials['api_key'] = os.environ['OS_PASSWORD']
        credentials['auth_url'] = os.environ['OS_AUTH_URL']
        credentials['project_id'] = os.environ['OS_TENANT_NAME']

        return nclient(**credentials)

    def _get_keystone_client(self):
        """ This converts env vars to local vasr & auths with OS """
        credentials = {}
        credentials['username'] = os.environ['OS_USERNAME']
        credentials['password'] = os.environ['OS_PASSWORD']
        credentials['auth_url'] = os.environ['OS_AUTH_URL']
        credentials['tenant_name'] = os.environ['OS_TENANT_NAME']

        return ksclient(**credentials)

    # Nova commands
    @botcmd(split_args_with=None)
    def nova_listservers(self, mess, args):
        """ This command gets all of the servers of a project """
        servers = self.novaclient.servers.list()
        serverlist = []
        for server in servers:
            serverlist.append(server.name)
        return serverlist

    @botcmd(split_args_with=None)
    def nova_getip(self, msg, args):
        input = args.pop()
        # @TODO: Need arg error handling here.

        # Lets search by id
        server = self._find_server_by_id(input)
        if server:
            return self._format_network(server)

        # Maybe input was a name...
        servers = self._find_server_by_name(input)
        if not servers:
            return "Sorry, that server does not exist"

        if servers > 1:
            output = {}
            for server in servers:
                # @TODO This is somewhat undesirable. Add interactivity
                output[server.id] = self._format_network(server)
            return str(output)
        else:
            # returned exactly 1 server
            return self._format_network(server)

    @botcmd(split_args_with=None)
    def nova_getmetadata(self, msg, args):
        input = args.pop()
        # @TODO: Need arg error handling here.

        # Lets search by id
        server = self._find_server_by_id(input)
        if server:
            self.log.info("FUCK: " + str(server.metadata))
            return server.metadata

        # Maybe input was a name...
        servers = self._find_server_by_name(input)
        if not servers:
            return "Sorry, that server does not exist"

        if servers > 1:
            output = {}
            for server in servers:
                # @TODO This is somewhat undesirable. Add interactivity
                self.log.info("FUCK: " + str(server.metadata))
                output[server.id] = server.metadata
            return str(output)
        else:
            # returned exactly 1 server
            return self._format_network(server)

    @botcmd(split_args_with=None)
    def nova_getcreator(self, msg, args):
        input = args.pop()
        # @TODO: Need arg error handling here.

        # Lets search by id
        server = self._find_server_by_id(input)
        if server:
            self.log.info(server.metadata)
            return server.metadata['created_by']

        # Maybe input was a name...
        servers = self._find_server_by_name(input)
        if not servers:
            return "Sorry, that server does not exist"

        if servers > 1:
            output = {}
            for server in servers:
                # @TODO This is somewhat undesirable. Add interactivity
                output[server.id] = server.metadata['created_by']
            return str(output)
        else:
            # returned exactly 1 server
            return self._format_network(server)

    @botcmd(split_args_with=None)
    def nova_getusers(self, msg, args):
        input = args.pop()
        # @TODO: Need arg error handling here.

        # Lets search by id
        server = self._find_server_by_id(input)
        if server:
            self.log.info("FUCK: " + str(server.metadata))
            return self._getusers(server.metadata)

        # Maybe input was a name...
        servers = self._find_server_by_name(input)
        if not servers:
            return "Sorry, that server does not exist"

        if servers > 1:
            output = {}
            for server in servers:
                # @TODO This is somewhat undesirable. Add interactivity
                output[server.id] = self._getusers(server.metadata)
            return str(output)
        else:
            # returned exactly 1 server
            return self._format_network(server)

    def _getusers(self, metadata):
        all_owners = [metadata['created_by'], metadata['sudo_users'], metadata['login_users'], metadata['sudo_groups'], metadata['login_groups'], metadata['sudo_groups']]
        owners_list = []

        # {u'sudo_users': u'DC1\\dbingham,DC1\\smcquaid', u'login_groups': u'DC1\\ac_devcloud,DC1\\su_devcloud', u'login_users': u'DC1\\dbingham,DC1\\jerobinson,DC1\\smcquaid', u'created_by': u'smcquaid', u'environment': u'DEV', u'sudo_groups': u'DC1\\su_devcloud', u'owning_group': u'26 - DEV-Private Cloud'}

        for item in all_owners:
            if item:
                pattern = re.compile("^\s+|DC1\\\\|\s*,\s*|DC1\\\\|\s+$")
                single_item_list = [x for x in pattern.split(item) if x]
                for single_item in single_item_list:
                    if single_item not in owners_list:
                        owners_list.append(single_item)

        self.log.info("INPUT: " + str(all_owners))
        self.log.info("OUTPUT: " + str(owners_list))
        return owners_list

    def _find_user_by_name(self, user):
        return user

    def _find_tenant_by_name(self, name):
        # Assuming tenant name is unique

        for tentant in self.tenantlist:
            if name == tentant.name:
                return tentant.id

        self.log.info("Tentant name: " + name + " was not found")
        # TODO Throw error
        return

    def _get_admin_user_role_id(self):
        return self._keystone_listroles().get('ProjectAdmin')

    @botcmd(split_args_with=None)
    def nova_forcedelete(self, msg, args):
        return "no"

    def _keystone_listroles(self):
        output = {}
        rolelist = self.keystoneclient.roles.list()
        for role in rolelist:
            output[role.name] = role.id
        return output

    @botcmd(split_args_with=None)
    def keystone_listroles(self, msg, args):
        return self._keystone_listroles()


    @botcmd(split_args_with=None)
    def keystone_listprojects(self, msg, args):
        output = {}
        for proj in self.tenantlist:
            output[proj.name] = proj.id

        return output


    @botcmd(split_args_with=None)
    def keystone_listprojectusers(self, msg, args):
        project_input = args.pop()

        project_id = self._find_tenant_by_name(project_input)
        return self.keystoneclient.tenants.list_users(project_id)


    @botcmd(split_args_with=None)
    def keystone_addadmintoproject(self, msg, args):
        project_input = args.pop() # stack = LIFO = reverse param ordering
        user_input = args.pop()


        user_id = self._find_user_by_name(user_input)
        project_id = self._find_tenant_by_name(project_input)
        admin_id = self._get_admin_user_role_id()

        # Add a user to a tenant with the given role.
        self.keystoneclient.roles.add_user_role(tenant=project_id, user=user_id, role=admin_id)
        return "Success"

    @botcmd(split_args_with=None)
    def keystone_removeadminfromproject(self, msg, args):
        project_input = args.pop() # stack = LIFO = reverse param ordering
        user_input = args.pop()

        user_id = self._find_user_by_name(user_input)
        project_id = self._find_tenant_by_name(project_input)
        admin_id = self._get_admin_user_role_id()

        # Remove a user from tenant with the given role.
        self.keystoneclient.roles.remove_user_role(tenant=project_id, user=user_id, role=admin_id)
        return "Success"


    # @TODO - Complete this
    @botcmd(split_args_with=None)
    def keystone_createproject(self, msg, args):
        project_name = args.pop()

        # keystone.tenants.create(tenant_name="openstackDemo", description="Default Tenant", enabled=True)
        return "Success"


    def callback_message(self, msg):
        if str(msg).find('cookie') != -1:
            self.send(msg.getFrom(), "What what somebody said cookie !?",
                      message_type=msg.getType())

            # @botcmd(split_args_with=None)
            # def nova(self, mess, args):
            #     '''Chef knife node ops. Params: [list|show <name>]'''
            #     try:
            #         verb = args.pop(0)
            #     except IndexError:
            #         raise Exception('Missing required verb. Choices are {}'
            #                         .format(', '.join(self.VERBS)))
            #     if verb not in self.VERBS:
            #         raise Exception('verb must be one of {}'
            #                         .format(', '.join(self.VERBS)))

            #     if verb == 'list':
            #         return self.node_list(mess)
            #     else:
            #         try:
            #             node_name = args.pop(0)
            #         except IndexError:
            #             raise Exception('Node name required')
            #         return self.node_show(mess, node_name)
