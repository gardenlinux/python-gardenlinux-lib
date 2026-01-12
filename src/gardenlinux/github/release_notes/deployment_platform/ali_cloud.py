# pyright: reportIncompatibleMethodOverride=false
from . import DeploymentPlatform


class AliCloud(DeploymentPlatform):
    def short_name(self) -> str:
        return "ali"

    def full_name(self) -> str:
        return "Alibaba Cloud"

    def image_extension(self) -> str:
        return "qcow2"
