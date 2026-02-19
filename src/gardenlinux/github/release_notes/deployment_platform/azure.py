from typing import Any, Dict

from . import DeploymentPlatform


class Azure(DeploymentPlatform):
    def short_name(self) -> str:
        return "azure"

    def full_name(self) -> str:
        return "Microsoft Azure"

    def image_extension(self) -> str:
        return "vhd"

    def published_images_by_regions(
        self, image_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        published_image_metadata = image_metadata.get("published_image_metadata", {})
        flavor_name = image_metadata["s3_key"].split("/")[-1]

        gallery_images = []
        marketplace_images = []

        for pset in published_image_metadata:
            if pset == "published_gallery_images":
                for gallery_image in published_image_metadata[pset]:
                    gallery_images.append(
                        {
                            "hyper_v_generation": gallery_image["hyper_v_generation"],
                            "azure_cloud": gallery_image["azure_cloud"],
                            "image_id": gallery_image["community_gallery_image_id"],
                        }
                    )

            if pset == "published_marketplace_images":
                for market_image in published_image_metadata[pset]:
                    marketplace_images.append(
                        {
                            "hyper_v_generation": market_image["hyper_v_generation"],
                            "urn": market_image["urn"],
                        }
                    )

        return {
            "flavor": flavor_name,
            "gallery_images": gallery_images,
            "marketplace_images": marketplace_images,
        }
