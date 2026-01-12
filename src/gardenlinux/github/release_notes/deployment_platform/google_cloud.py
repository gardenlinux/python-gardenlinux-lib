# pyright: reportIncompatibleMethodOverride=false
from typing import Any, Dict

from . import DeploymentPlatform


class GoogleCloud(DeploymentPlatform):
    def short_name(self) -> str:
        return "gcp"

    def full_name(self) -> str:
        return "Google Cloud Platform"

    def image_extension(self) -> str:
        return "gcpimage.tar.gz"

    def published_images_by_regions(
        self, image_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        published_image_metadata = image_metadata["published_image_metadata"]
        flavor_name = image_metadata["s3_key"].split("/")[-1]

        details = {}
        if "gcp_image_name" in published_image_metadata:
            details["image_name"] = published_image_metadata["gcp_image_name"]
        if "gcp_project_name" in published_image_metadata:
            details["project"] = published_image_metadata["gcp_project_name"]
        details["availability"] = "Global (all regions)"

        return {"flavor": flavor_name, "details": details}
