# pyright: reportIncompatibleMethodOverride=false
from .openstack import OpenStack


class OpenStackBareMetal(OpenStack):
    def short_name(self):
        return "openstackbaremetal"

    def full_name(self):
        return "OpenStack Baremetal"
