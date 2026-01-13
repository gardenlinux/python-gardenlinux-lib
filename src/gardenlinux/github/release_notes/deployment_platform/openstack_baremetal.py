# pyright: reportIncompatibleMethodOverride=false
from .openstack import OpenStack


class OpenStackBareMetal(OpenStack):
    def short_name(self) -> str:
        return "openstackbaremetal"

    def full_name(self) -> str:
        return "OpenStack Baremetal"
