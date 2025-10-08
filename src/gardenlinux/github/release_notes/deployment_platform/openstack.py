from . import DeploymentPlatform


class OpenStack(DeploymentPlatform):
    def short_name(self):
        return "openstack"

    def full_name(self):
        return "OpenStack"

    def published_images_by_regions(self, image_metadata):
        published_image_metadata = image_metadata["published_image_metadata"]
        flavor_name = image_metadata["s3_key"].split("/")[-1]

        regions = []
        if "published_openstack_images" in published_image_metadata:
            for image in published_image_metadata["published_openstack_images"]:
                regions.append(
                    {
                        "region": image["region_name"],
                        "image_id": image["image_id"],
                        "image_name": image["image_name"],
                    }
                )

        return {"flavor": flavor_name, "regions": regions}
