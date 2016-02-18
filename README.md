err-helloworld
--------------

This plugin allows openstack admins to administer openstack and get trivial information.

# TODO: Design & architecture
    * Setup redis backend/Datastore
    * Store logs in platform store
    * Setup metrics/alerts
    * Build two-person approval plugin
    * Setup locking of commands during critical situations
    * Figure out caching strategy for openstack
    * Allow norm to update himself
    * Save current configuration to config.py or elsewhere.
    * Setup HA norm. Active-Active/leader election
    * Dockerize norm
    * Setup unit testing framework
    * Setup standardized plugin showing all features simply.
    * Watch logs on specific servers

# Future plugins, commands, and features

## err-puppet
These will run puppet on the specified environment. Protections will need to be added in here
    * `!lock puppet`  # Locks all puppet-commands
    * `!puppet clean <env>` # make sure everything is clean and delete any hand-modified code
    * `!puppet run <env>`  # Run puppet on specific environment.
    * `!puppet kick|reboot <env>`  # Reboot specific environment.
    * `!puppet shell <command>`  # Run specific commands on Map/Cap servers.

## err-gd-deploy
These are idealized commands of which we will not implement halfway. Works or nothing.

    * `!devstack up [--version <version>] [--users <users>]  # Spin up devstack for developers
    * `!deploy <product> <environment>`  # Deploy product to environment
    * `!deploy rollback <product> <env> [--version <version>]  # Rollback to specific version
    * `!redalert [<env>]`  # Procedures + notifications + automation for when something breaks.
    * `!monitorincident <incident_id> <time_delay>`  # Poll for incident status every X seconds

## err-gd-patching
    * `!gdpatching start <patching_job_id` # Notify users of vms affected by patching in slack.
    * `!gdpatching stop <patching_job_id>`  # Notify that patching is over. Clean up as necessary.
    * `!gdpatching run <patching_job_id>`  # Future one liner which will do everything for you.

## err-oncall
    * `!oncall`  # gets primary oncall name and phone
    * `!oncall secondary`  # gets primary oncall name and phone

## err-tour
    * `!tour`  # starts and interactive tour in a private message, ala: https://github.com/taoistmath/err-odysseus/blob/master/guidedTour.py

## err-agile
    * `!agile standup`  # Notify channel for daily standups/meetings.
    * `!agile zoom`  # Post zoom link.
    * `!jira <ticket#>  # gets subject and link to ticket
    * `!jira addstory|addfeature <text to add to backlog>`  # add a story/feature to the backlog
    * `!git merge <repo> <PR ID>  # Merge PR if it has a +1
    * `!jenkins run <jobname>`  # Run specific jenkins job
    * `!jenkins listjobs`  # List all jobs
    * `!jenkins watch [--job <job_id>] [--build <build_id]`  # Notify channel of repeated build failures/watch a job

## err-secure
    * `!approve <command_identifier>`  # Nuclear launch code/Dual big red buttons (two people must approve certain commands)
    * `!restrict <command_name> <group of people>`  # Restrict specific or all commands to cloud admins only.
    * `!admins add <DC1 Username>`  # Add a person to the admins list
    * `!admins remove <DC1 Username>`  # Add a person to the admins list

## err-networking
    * `!networking debug <destination>`  # Networking debugging
    * `!dns <name>`  # searches the search domains for the hostname and returns the fqdn
    * `!dns <ip>`  # does reverse DNS search for the ip and returns the fqdn

## err-gddy
    * `!smdb debug`  # SMDB Client Testing
    * `!srapi debug`  # SR API testing
    * `!ad islockedout <username>`  # Check if user is locked out
    * `!ad remove <hostname>`  # Remove ad hostname entry

## err-openstack
    * `!nova status <vmID>`  # Check status of vm
    * `!nova boot <name> <env> <users>`  # Create vm in specific environment for testing.
    * `!nova gethypervisor <vm_uuid>`  # Get the hypervisor fqdn of the VM
    * `!nova reboot <vmID>`  # Reboot vm
    * `!nova nuke|delete|forcedelete <vmID>`  # Destroy vm no matter what
    * `!openstack setenv <env>`  # Allow norm to switch environments temporarily.
    * `!openstack debugip <ip>`  # Look for the route, look for the allowed address pair on the vm
