# -*- coding: utf-8 -*-

# for reference:
#   https://json-schema.org/understanding-json-schema/reference/object

# TODO: add more schemas, and validate dicts with schemas before accessing them.

schema_url = "http://json-schema.org/draft-07/schema"

platform_properties = {
    "architecture": {"type": "string"},
    "os": {"type": "string"},
    "os.version": {"type": "string"},
    "variant": {"type": "string"},
}

manifest_meta_properties = {
    "mediaType": {"type": "string"},
    "platform": {"type": "object", "properties": platform_properties},
}

index_properties = {
    "schemaVersion": {"type": "number"},
    "mediaType": {"type": "string"},
    "subject": {"type": ["null", "object"]},
    "manifests": {"type": "array", "items": manifest_meta_properties},
    "annotations": {"type": ["object", "null", "array"]},
}


index = {
    "$schema": schema_url,
    "title": "Index Schema",
    "type": "object",
    "required": [
        "schemaVersion",
        "manifests",
        "mediaType",
    ],
    "properties": index_properties,
    "additionalProperties": True,
}

empty_platform = {
    "architecture": "",
    "os": "gardenlinux",
    "os.version": "experimental",
}

empty_manifest_metadata = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "",
    "size": 0,
    "annotations": {},
}

empty_index = {
    "schemaVersion": 2,
    "mediaType": "application/vnd.oci.image.index.v1+json",
    "manifests": [],
}
