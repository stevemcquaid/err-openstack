from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd
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

    @botcmd(split_args_with=None, admin_only=True)
    def openstack_refreshcache(self, msg, args):
        """ Refreshes the nova & keystone clients and the server & tenant lists """
        result = self._refreshcache()
        if self._refreshcache():
            return "Success"
        else:
            return result

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

    def _get_nova_client(self, project_name=None):
        """ This converts env vars to local vasr & auths with OS """
        credentials = {}
        credentials['version'] = '2'
        credentials['username'] = os.environ['OS_USERNAME']
        credentials['api_key'] = os.environ['OS_PASSWORD']
        credentials['auth_url'] = os.environ['OS_AUTH_URL']
        # not this is not a mis-match, novaclient is stupid
        if project_name:
            credentials['project_id'] = project_name
        else:
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


    # Helpers
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

    def _getusers(self, metadata):
        all_owners = [metadata['created_by'], metadata['sudo_users'], metadata['login_users'], metadata['sudo_groups'], metadata['login_groups'], metadata['sudo_groups']]
        owners_list = []

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
        # @TODO - need to add validation here so the script quickly fails for invalid username
        return user

    def _find_tenant_by_name(self, name):
        # Assuming tenant name is unique

        for tenant in self.tenantlist:
            if name == tenant.name:
                return tenant

        self.log.info("Tenant name: " + name + " was not found")
        # TODO Throw error
        return

    def _find_tenant_by_id(self, id):
        for tenant in self.tenantlist:
            if id == tenant.id:
                return tenant

        self.log.info("Tenant id: " + id + " was not found")
        # TODO Throw error
        return

    def _get_admin_user_role_id(self):
        return self._keystone_listroles().get('ProjectAdmin')

    def _append_user_to_server_meta_item(self, server_obj, metadata_key, value_to_append):
        item = server_obj.metadata.get(metadata_key)
        item += ',DC1\\' + value_to_append
        self.novaclient.servers.set_meta_item(server=server_obj, key=metadata_key, value=item)

    # Nova commands
    @arg_botcmd('--project-id', dest='project_id', type=str, default=None)
    @arg_botcmd('--project-name', dest='project_name', type=str, default=None)
    def keystone_listservers(self, mess, project_id=None, project_name=None):
        """ Gets all servers of a given project"""

        # Need to make sure we have at least one param given
        if (not project_name) and (not project_id):
            return "Too few arguments given"

        # Get tenant from name
        if project_name:
            tenant = self._find_tenant_by_name(project_name)
            if not tenant:
                return "Sorry I could not find project_name: %s" % project_name

        # Get tenant from id
        if project_id:
            tenant = self._find_tenant_by_id(project_id)
            if not tenant:
                return "Sorry I could not find project_id: %s" % project_id

        novaclient = self._get_nova_client(tenant.name)
        serverlist = novaclient.servers.list()

        output = []
        for server in serverlist:
            output.append(server.name)

        return output if output else "Looks like I could not find anything. Sorry."


    @arg_botcmd('--server-id', dest='server_id', type=str, default=None)
    @arg_botcmd('--server-name', dest='server_name', type=str, default=None)
    def nova_getip(self, msg, server_name=None, server_id=None):
        """ Returns the ip(s) of a given server. """

        # Need to make sure we have at least one param given
        if (not server_name) and (not server_id):
            return "Too few arguments given"

        # Lets get the server if id
        if server_id:
            server = self._find_server_by_id(server_id)
            return self._format_network(server) if server else "Sorry, that server does not exist"

        # Input must have been a name...
        servers = self._find_server_by_name(server_name)
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
            return self._format_network(servers[0])

    @arg_botcmd('--server-id', dest='server_id', type=str, default=None)
    @arg_botcmd('--server-name', dest='server_name', type=str, default=None)
    def nova_getmetadata(self, msg, server_id=None, server_name=None):
        """ Returns the metadata of a given server. """

        # Need to make sure we have at least one param given
        if (not server_name) and (not server_id):
            return "Too few arguments given"

        # Lets search by id
        if server_id:
            server = self._find_server_by_id(server_id)
            return server.metadata if server else "Sorry, that server does not exist"

        # Maybe input was a name...
        servers = self._find_server_by_name(server_name)
        if not servers:
            return "Sorry, that server does not exist"

        if servers > 1:
            output = {}
            for server in servers:
                # @TODO This is somewhat undesirable. Add interactivity
                output[server.id] = server.metadata
            return str(output)
        else:
            # returned exactly 1 server
            return servers[0].metadata

    @arg_botcmd('--server-id', dest='server_id', type=str, default=None)
    @arg_botcmd('--server-name', dest='server_name', type=str, default=None)
    def nova_getcreator(self, msg, server_id=None, server_name=None):
        """ Gets creator of server from metadata. """

        # Need to make sure we have at least one param given
        if (not server_name) and (not server_id):
            return "Too few arguments given"

        # Lets search by id
        if server_id:
            server = self._find_server_by_id(server_id)
            return server.metadata if server else "Sorry, that server does not exist"

        # Maybe input was a name...
        servers = self._find_server_by_name(server_name)
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
            return servers[0].metadata['created_by']

    @arg_botcmd('--server-id', dest='server_id', type=str, default=None)
    @arg_botcmd('--server-name', dest='server_name', type=str, default=None)
    def nova_getusers(self, msg, server_id=None, server_name=None):
        """ Gets list of all users/groups of server. """

        # Need to make sure we have at least one param given
        if (not server_name) and (not server_id):
            return "Too few arguments given"

        # Lets search by id
        if server_id:
            server = self._find_server_by_id(server_id)
            return server.metadata if server else "Sorry, that server does not exist"

        # Maybe input was a name...
        servers = self._find_server_by_name(server_name)
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
            return self._getusers(servers[0].metadata)


    def _keystone_listroles(self):
        output = {}
        rolelist = self.keystoneclient.roles.list()
        for role in rolelist:
            output[role.name] = role.id
        return output

    @botcmd
    def keystone_listroles(self, msg, args):
        """ Gets all user-roles. """
        return self._keystone_listroles()


    @botcmd
    def keystone_listprojects(self, msg, args):
        """ Gets list of projects in current environment. """
        output = {}
        for proj in self.tenantlist:
            output[proj.name] = proj.id

        return output

    @arg_botcmd('--project-id', dest='project_id', type=str, default=None)
    @arg_botcmd('--project-name', dest='project_name', type=str, default=None)
    def keystone_listprojectusers(self, msg, project_id=None, project_name=None):
        """ Gets list of users of project. EX: !keystone listprojects <name>"""
        # Need to make sure we have at least one param given
        if (not project_name) and (not project_id):
            return "Too few arguments given"

        # Lets get the project if id
        if project_id:
            project = self._find_tenant_by_id(project_id) #This is unnecessary but I'll keep it for now.
            return self.keystoneclient.tenants.list_users(project.id) if project else "Sorry, that project does not exist"

        if project_name:
            project = self._find_tenant_by_name(project_name)
            return self.keystoneclient.tenants.list_users(project.id) if project else "Sorry, that project does not exist"

        self.log.error("No project_name or id was given. Logically impossible?")
        return "Well... it looks like I am on fire"

    @botcmd(admin_only=True)
    @arg_botcmd('--user-name', type=str)
    @arg_botcmd('--project-id', dest='project_id', type=str, default=None)
    @arg_botcmd('--project-name', dest='project_name', type=str, default=None)
    def keystone_addadmintoproject(self, msg, user_name=None, project_id=None, project_name=None):
        """ Add user to project. EX: !keystone addadmintoproject <username> <projectname> """
        # Need to make sure we have at least one param given
        if (not project_name) and (not project_id):
            return "Too few arguments given"

        if not user_name:
            return "Too few arguments given"

        user_id = self._find_user_by_name(user_name)
        admin_id = self._get_admin_user_role_id()

        if project_id:
            project = self._find_tenant_by_id(project_id)

        if project_name:
            project = self._find_tenant_by_name(project_name)

        # Fail fast
        if not project:
            return "Project not found"

        # We should be good, so lets add a user to a tenant with the given role.
        self.keystoneclient.roles.add_user_role(tenant=project.id, user=user_id, role=admin_id)
        # We modified stuff so we need to refresh the cache
        self._refreshcache()
        return "Success"


    @botcmd(admin_only=True)
    @arg_botcmd('--user-name', type=str)
    @arg_botcmd('--project-id', dest='project_id', type=str, default=None)
    @arg_botcmd('--project-name', dest='project_name', type=str, default=None)
    def keystone_removeadminfromproject(self, msg, user_name=None, project_id=None, project_name=None):
        """ Remove user from project."""

        # Need to make sure we have at least one param given
        if (not project_name) and (not project_id):
            return "Too few arguments given"

        if not user_name:
            return "Too few arguments given"

        user_id = self._find_user_by_name(user_name)
        admin_id = self._get_admin_user_role_id()

        if project_id:
            project = self._find_tenant_by_id(project_id)

        if project_name:
            project = self._find_tenant_by_name(project_name)

        # Fail fast
        if not project:
            return "Project not found"

        # We should be good, so lets add a user to a tenant with the given role.
        self.keystoneclient.roles.remove_user_role(tenant=project.id, user=user_id, role=admin_id)
        # We modified stuff so we need to refresh the cache
        self._refreshcache()
        return "Success"


    @botcmd(admin_only=True)
    @arg_botcmd('--user-name', type=str)
    @arg_botcmd('--server-id', dest='server_id', type=str, default=None)
    @arg_botcmd('--server-name', dest='server_name', type=str, default=None)
    def nova_addadmintoserver(self, msg, user_name=None, server_id=None, server_name=None):
        """ Add user to server. """

        # Need to make sure we have at least one param given
        if (not server_name) and (not server_id):
            return "Too few arguments given"

        if not user_name:
            return "Too few arguments given"

        user_id = self._find_user_by_name(user_name)
        admin_id = self._get_admin_user_role_id()

        if server_id:
            server = self._find_server_by_id(server_id)
            if not server:
                self.error.info("There is a problem here")
                return "Sorry, server_id: %s does not exist" % server_id

            self._append_user_to_server_meta_item(server_obj=server, metadata_key='login_users', value_to_append=user_id)
            self._append_user_to_server_meta_item(server_obj=server, metadata_key='sudo_users', value_to_append=user_id)
            # We modified stuff so we need to refresh the cache
            self._refreshcache()
            return "Success"

        # Maybe server input was a name...
        if server_name:
            servers = self._find_server_by_name(server_name)
            if not servers:
                self.error.info("There is a problem here")
                return "Sorry, server_name: %s does not exist" % server_name
            if len(servers) > 1:
                return "Sorry, there is more than one server with that name. Please use --server_id"
            if len(servers) == 1:
                for server_obj in servers:
                    self._append_user_to_server_meta_item(server_obj=server_obj, metadata_key='login_users', value_to_append=user_id)
                    self._append_user_to_server_meta_item(server_obj=server_obj, metadata_key='sudo_users', value_to_append=user_id)
                    # We modified stuff so we need to refresh the cache
                    self._refreshcache()
                    return "Success"

        self.log.error("No server_name or server_id was given. Logically impossible?")
        return "Well... it looks like I am on fire"


    def _remove_user_from_server_meta_item(self, server_obj, metadata_key, value_to_remove):
        items = server_obj.metadata.get(metadata_key).split(",")
        items.remove('DC1\\' + value_to_remove)
        new_value = ",".join(items)
        self.novaclient.servers.set_meta_item(server=server_obj, key=metadata_key, value=new_value)


    @botcmd(admin_only=True)
    @arg_botcmd('--user-name', type=str)
    @arg_botcmd('--server-id', dest='server_id', type=str, default=None)
    @arg_botcmd('--server-name', dest='server_name', type=str, default=None)
    def nova_removeadminfromserver(self, msg, user_name=None, server_id=None, server_name=None):
        """ Remove user from server. """

        # Need to make sure we have at least one param given
        if (not server_name) and (not server_id):
            return "Too few arguments given"

        if not user_name:
            return "Too few arguments given"

        user_id = self._find_user_by_name(user_name)
        admin_id = self._get_admin_user_role_id()

        if server_id:
            server = self._find_server_by_id(server_id)
            if not server:
                self.error.info("There is a problem here")
                return "Sorry, server_id: %s does not exist" % server_id

            self._remove_user_from_server_meta_item(server_obj=server, metadata_key='login_users', value_to_remove=user_id)
            self._remove_user_from_server_meta_item(server_obj=server, metadata_key='sudo_users', value_to_remove=user_id)
            # We modified stuff so we need to refresh the cache
            self._refreshcache()
            return "Success"

        # Maybe server input was a name...
        if server_name:
            servers = self._find_server_by_name(server_name)
            if not servers:
                self.error.info("There is a problem here")
                return "Sorry, server_name: %s does not exist" % server_name
            if len(servers) > 1:
                return "Sorry, there is more than one server with that name. Please use --server_id"
            if len(servers) == 1:
                for server_obj in servers:
                    self._remove_user_from_server_meta_item(server_obj=server_obj, metadata_key='login_users', value_to_remove=user_id)
                    self._remove_user_from_server_meta_item(server_obj=server_obj, metadata_key='sudo_users', value_to_remove=user_id)
                    # We modified stuff so we need to refresh the cache
                    self._refreshcache()
                    return "Success"

        self.log.error("No server_name or server_id was given. Logically impossible?")
        return "Well... it looks like I am on fire"


    def _find_server_by_ip(self, server_ip):
        found_servers = []
        for server in self.serverlist:
            if server_ip in str(server.networks.items()):
                found_servers.append(server)
                self.log.error("Server name: %s" % (server.name) )

        return found_servers

    def _format_server_print(self, server):
        return "Name: %s, UUID: %s" % (server.name, server.id)

    @arg_botcmd('--server-ip', type=str)
    def nova_findserverbyip(self, msg, server_ip=None):
        # Need to make sure we have at least one param given
        if (not server_ip):
            return "Too few arguments given"

        # Maybe input was a name...
        servers = self._find_server_by_ip(server_ip)
        if not servers:
            return "Sorry, we could not find a server with that static IP address"

        if servers > 1:
            output = {}
            for server in servers:
                # @TODO This is somewhat undesirable. Add interactivity
                output[server.id] = self._format_server_print(server)
            return str(output)
        else:
            # returned exactly 1 server
            return self._format_server_print(servers[0])

    # @botcmd(split_args_with=None)
    # def keystone_createproject(self, msg, args):
    #     """ Does nothing currently """
    #     # project_name = args.pop()

    #     # keystone.tenants.create(tenant_name="openstackDemo", description="Default Tenant", enabled=True)

    #     # We modified stuff so we need to refresh the cache
    #     # self._refreshcache()
    #     # return "Success"
    #     pass

    # @TODO - Complete this
    # @botcmd(split_args_with=None)
    # def ad_clearhostname(self, msg, args):
    #     """ Does nothing currently """
    #     # hostname = args.pop()
    #     # TODO Clear ad hostname
    #     pass

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
