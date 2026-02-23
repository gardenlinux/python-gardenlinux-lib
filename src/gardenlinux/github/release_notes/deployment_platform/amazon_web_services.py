from typing import Any, Dict

from . import DeploymentPlatform


class AmazonWebServices(DeploymentPlatform):
    def short_name(self) -> str:
        return "aws"

    def full_name(self) -> str:
        return "Amazon Web Services"

    def published_images_by_regions(
        self, image_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        published_image_metadata = image_metadata.get("published_image_metadata", {})
        flavor_name = image_metadata["s3_key"].split("/")[-1]

        regions = []
        for pset in published_image_metadata:
            for p in published_image_metadata[pset]:
                regions.append({"region": p["aws_region_id"], "image_id": p["ami_id"]})

        return {"flavor": flavor_name, "regions": regions}
