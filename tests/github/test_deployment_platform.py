from gardenlinux.github.release import DeploymentPlatform


def test_default_get_file_extension_for_deployment_platform() -> None:
    assert (
        DeploymentPlatform.new_instance({"platform": "generic"}).image_extension
        == "raw"
    )
