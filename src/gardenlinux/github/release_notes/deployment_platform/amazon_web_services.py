from . import DeploymentPlatform


class AmazonWebServices(DeploymentPlatform):
    def full_name(self):
        return "Amazon Web Services"
