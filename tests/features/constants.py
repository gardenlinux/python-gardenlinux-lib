from gardenlinux.constants import (
    GL_BUG_REPORT_URL,
    GL_DISTRIBUTION_NAME,
    GL_HOME_URL,
    GL_RELEASE_ID,
    GL_SUPPORT_URL,
)


def generate_container_amd64_release_metadata(version, commit_hash):
    return f"""
ID={GL_RELEASE_ID}
NAME="{GL_DISTRIBUTION_NAME}"
PRETTY_NAME="{GL_DISTRIBUTION_NAME} {version}"
IMAGE_VERSION={version}
VARIANT_ID="container-amd64"
HOME_URL="{GL_HOME_URL}"
SUPPORT_URL="{GL_SUPPORT_URL}"
BUG_REPORT_URL="{GL_BUG_REPORT_URL}"
GARDENLINUX_CNAME="container-amd64-{version}-{commit_hash}"
GARDENLINUX_FEATURES="_slim,base,container"
GARDENLINUX_FEATURES_PLATFORM="container"
GARDENLINUX_FEATURES_ELEMENTS="base"
GARDENLINUX_FEATURES_FLAGS="_slim"
GARDENLINUX_PLATFORM_VARIANT=""
GARDENLINUX_VERSION="{version}"
GARDENLINUX_COMMIT_ID="{commit_hash}"
GARDENLINUX_COMMIT_ID_LONG="{commit_hash}"
""".strip()
