from . import DeploymentPlatform


class AliCloud(DeploymentPlatform):
    def full_name(self):
        return "Alibaba Cloud"

    def image_extension(self):
        return "qcow2"
