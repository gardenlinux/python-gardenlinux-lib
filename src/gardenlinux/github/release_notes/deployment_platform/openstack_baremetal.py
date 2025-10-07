from .openstack import OpenStack


class OpenStackBareMetal(OpenStack):
    def full_name(self):
        return "OpenStack Baremetal"
