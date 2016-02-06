err-helloworld
--------------

This plugin allows openstack admins to administer openstack and get trivial information.

# TODO


# DEV NOTES

keystone - project - user auth


nova - compute - vm

get uuid of vm


INPUT = VM UUID
(nova show UUID).get('tenant_id')

keystone user-role-add --user-id dtischler --tenant-id 2e08fb6e2b4d4a1aa54476398c2f9769 --role ProjectAdmin


