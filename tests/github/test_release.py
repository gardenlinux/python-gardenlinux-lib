import pytest
import requests
import requests_mock

from gardenlinux.github.release import Release, write_to_release_id_file

from ..constants import (
    TEST_GARDENLINUX_COMMIT,
    TEST_GARDENLINUX_RELEASE,
)

REPO="""
[
  {
    "id": 1,
    "node_id": "test",
    "name": "python-gardenlinux-lib",
    "full_name": "gardenlinux/python-gardenlinux-lib",
    "owner":{},
    "private": false,
    "html_url": "https://github.com/gardenlinux/python-gardenlinux-lib",
    "description": "Happily copied from REST API endpoints for repositories @ github.com",
    "fork": false,
    "url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib",
    "archive_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/{archive_format}{/ref}",
    "assignees_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/assignees{/user}",
    "blobs_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/git/blobs{/sha}",
    "branches_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/branches{/branch}",
    "collaborators_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/collaborators{/collaborator}",
    "comments_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/comments{/number}",
    "commits_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/commits{/sha}",
    "compare_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/compare/{base}...{head}",
    "contents_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/contents/{+path}",
    "contributors_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/contributors",
    "deployments_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/deployments",
    "downloads_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/downloads",
    "events_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/events",
    "forks_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/forks",
    "git_commits_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/git/commits{/sha}",
    "git_refs_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/git/refs{/sha}",
    "git_tags_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/git/tags{/sha}",
    "git_url": "git:github.com/gardenlinux/python-gardenlinux-lib.git",
    "issue_comment_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/issues/comments{/number}",
    "issue_events_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/issues/events{/number}",
    "issues_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/issues{/number}",
    "keys_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/keys{/key_id}",
    "labels_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/labels{/name}",
    "languages_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/languages",
    "merges_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/merges",
    "milestones_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/notifications{?since,all,participating}",
    "pulls_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/pulls{/number}",
    "releases_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/releases{/id}",
    "ssh_url": "git@github.com:gardenlinux/python-gardenlinux-lib.git",
    "stargazers_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/stargazers",
    "statuses_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/statuses/{sha}",
    "subscribers_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/subscribers",
    "subscription_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/subscription",
    "tags_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/tags",
    "teams_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/teams",
    "trees_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/git/trees{/sha}",
    "clone_url": "https://github.com/gardenlinux/python-gardenlinux-lib.git",
    "mirror_url": "git:git.example.com/gardenlinux/python-gardenlinux-lib",
    "hooks_url": "https://api.github.com/repos/gardenlinux/python-gardenlinux-lib/hooks",
    "svn_url": "https://svn.github.com/gardenlinux/python-gardenlinux-lib",
    "homepage": "https://github.com",
    "language": null,
    "forks_count": 0,
    "stargazers_count": 0,
    "watchers_count": 0,
    "size": 1,
    "default_branch": "main",
    "open_issues_count": 0,
    "is_template": false,
    "topics": [],
    "has_issues": true,
    "has_projects": true,
    "has_wiki": true,
    "has_pages": true,
    "has_downloads": true,
    "has_discussions": true,
    "archived": false,
    "disabled": false,
    "visibility": "public",
    "pushed_at": "2011-01-26T19:06:43Z",
    "created_at": "2011-01-26T19:01:12Z",
    "updated_at": "2011-01-26T19:14:43Z",
    "permissions": {
      "admin": false,
      "push": false,
      "pull": true
    },
    "security_and_analysis": {}
  }
]
"""


def test_Release_create_needs_github_token():
    with (
        requests_mock.Mocker(),
        pytest.raises(ValueError, match="GITHUB_TOKEN environment variable not set"),
    ):
        _ = Release("gardenlinux", "gardenlinux")


def test_Release_raise_on_failure(caplog, github_token):
    with requests_mock.Mocker() as m:
        release = Release("gardenlinux", "gardenlinux", token="test")

        release.tag = TEST_GARDENLINUX_RELEASE
        release.commitish = TEST_GARDENLINUX_COMMIT
        release.is_latest = (False,)
        release.body = ""

        with pytest.raises(requests.exceptions.HTTPError):
            m.get(
                "//api.github.com:443/repos/gardenlinux/gardenlinux",
                text=REPO,
                status_code=200,
            )

            m.post(
                "//api.github.com:443/repos/gardenlinux/gardenlinux/releases",
                text="{}",
                status_code=503,
            )

            release.create()
        assert any(
            "Failed to create release" in record.message for record in caplog.records
        ), "Expected a failure log record"


def test_Release(caplog, github_token):
    with requests_mock.Mocker() as m:
        release = Release("gardenlinux", "gardenlinux", token="test")

        release.tag = TEST_GARDENLINUX_RELEASE
        release.commitish = TEST_GARDENLINUX_COMMIT
        release.is_latest = (False,)
        release.body = ""

        m.get(
            "//api.github.com:443/repos/gardenlinux/gardenlinux",
            text=REPO,
            status_code=200,
        )

        m.post(
            "//api.github.com:443/repos/gardenlinux/gardenlinux/releases",
            text='{"id": 101}',
            status_code=201,
        )

        assert release.create() == 101
        assert any(
            "Release created successfully" in record.message
            for record in caplog.records
        ), "Expected a success log record"


def test_write_to_release_id_file(release_id_file):
    write_to_release_id_file(TEST_GARDENLINUX_RELEASE)
    assert release_id_file.read_text() == TEST_GARDENLINUX_RELEASE


def test_write_to_release_id_file_broken_file_permissions(release_id_file, caplog):
    release_id_file.touch(0)  # this will make the file unwritable

    with pytest.raises(SystemExit):
        write_to_release_id_file(TEST_GARDENLINUX_RELEASE)
    assert any("Could not create" in record.message for record in caplog.records), (
        "Expected a failure log record"
    )
