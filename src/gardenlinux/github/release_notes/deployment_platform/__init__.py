from gardenlinux.constants import GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME


class DeploymentPlatform:
    artifacts_bucket_name = GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME

    def short_name(self):
        return "generic"

    def full_name(self):
        return "Generic Deployment Platform"

    def published_images_by_regions(self, image_metadata):
        published_image_metadata = image_metadata["published_image_metadata"]
        flavor_name = image_metadata["s3_key"].split("/")[-1]

        regions = []
        for pset in published_image_metadata:
            for p in published_image_metadata[pset]:
                regions.append({"region": p["region_id"], "image_id": p["image_id"]})

        return {"flavor": flavor_name, "regions": regions}

    def image_extension(self):
        return "raw"

    def artifact_for_flavor(self, flavor, markdown_format=True):
        base_url = (
            f"https://{self.__class__.artifacts_bucket_name}.s3.amazonaws.com/objects"
        )
        filename = f"{flavor}.{self.image_extension()}"
        download_url = f"{base_url}/{flavor}/{filename}"
        if markdown_format:
            return f"[{filename}]({download_url})"
        else:
            return download_url

    def region_details(self, image_metadata):
        """
        Generate the detailed region information for the collapsible section
        """
        details = ""

        match self.published_images_by_regions(image_metadata):
            case {"regions": regions}:
                for region in regions:
                    match region:
                        case {
                            "region": region_name,
                            "image_id": image_id,
                            "image_name": image_name,
                        }:
                            details += (
                                f"**{region_name}:** {image_id} ({image_name})<br>"
                            )
                        case {"region": region_name, "image_id": image_id}:
                            details += f"**{region_name}:** {image_id}<br>"
            case {"details": details_dict}:
                for key, value in details_dict.items():
                    details += f"**{key.replace('_', ' ').title()}:** {value}<br>"
            case {
                "gallery_images": gallery_images,
                "marketplace_images": marketplace_images,
            }:
                if gallery_images:
                    details += "**Gallery Images:**<br>"
                    for img in gallery_images:
                        details += f"• {img['hyper_v_generation']} ({img['azure_cloud']}): {img['image_id']}<br>"
                if marketplace_images:
                    details += "**Marketplace Images:**<br>"
                    for img in marketplace_images:
                        details += f"• {img['hyper_v_generation']}: {img['urn']}<br>"
            case {"gallery_images": gallery_images}:
                details += "**Gallery Images:**<br>"
                for img in gallery_images:
                    details += f"• {img['hyper_v_generation']} ({img['azure_cloud']}): {img['image_id']}<br>"
            case {"marketplace_images": marketplace_images}:
                details += "**Marketplace Images:**<br>"
                for img in marketplace_images:
                    details += f"• {img['hyper_v_generation']}: {img['urn']}<br>"

        return details

    def summary_text(self, image_metadata):
        """
        Generate the summary text for the collapsible section
        """
        match self.published_images_by_regions(image_metadata):
            case {"regions": regions}:
                count = len(regions)
                return f"{count} regions"
            case {"details": _}:
                return "Global availability"
            case {
                "gallery_images": gallery_images,
                "marketplace_images": marketplace_images,
            }:
                gallery_count = len(gallery_images)
                marketplace_count = len(marketplace_images)
                return (
                    f"{gallery_count} gallery + {marketplace_count} marketplace images"
                )
            case {"gallery_images": gallery_images}:
                gallery_count = len(gallery_images)
                return f"{gallery_count} gallery images"
            case {"marketplace_images": marketplace_images}:
                marketplace_count = len(marketplace_images)
                return f"{marketplace_count} marketplace images"
            case _:
                return "Details available"
