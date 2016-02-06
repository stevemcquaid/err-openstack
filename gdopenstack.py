from errbot import BotPlugin, botcmd
from novaclient.client import Client
import os
import argparse
import json


class GDOpenstack(BotPlugin):
    def activate(self):
        self.novaclient = None
        self.serverlist = None

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
        # Get a list of running servers.
        self.serverlist = \
            self.novaclient.servers.list(
                search_opts=dict(all_tenants=True))

        # @TODO: Can send callback if desired
        # DEBUG: Cache refreshed
        return True

    @botcmd(split_args_with=None)
    def hello(self, msg, args):
        """Say hello to someone"""
        return "Hello, " + format(msg.frm)

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

        return Client(**credentials)

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
    def nova_forcedelete(self, msg, args):
        pass

    @botcmd(split_args_with=None)
    def nova_getcreator(self, msg, args):
        input = args.pop()
        # @TODO: Need arg error handling here.

        # Lets search by id
        server = self._find_server_by_id()
        if server:
            meta = json.loads(server.metadata)

        # Maybe input was a name...
        servers = self._find_server_by_name()
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
