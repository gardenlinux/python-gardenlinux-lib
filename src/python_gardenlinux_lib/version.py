import re
import subprocess
from datetime import datetime, timezone
import requests
from pathlib import Path

from .logger import LoggerSetup
from .features.parse_features import get_features


class Version:
    """Handles version-related operations for Garden Linux."""

    def __init__(self, git_root: Path, logger=None):
        """Initialize Version handler.

        Args:
            git_root: Path to the Git repository root
            logger: Optional logger instance
        """
        self.git_root = git_root
        self.log = logger or LoggerSetup.get_logger("gardenlinux.version")
        self.start_date = "Mar 31 00:00:00 UTC 2020"

    def get_minor_from_repo(self, major):
        """Check repo.gardenlinux.io for highest available suite minor for given major.

        Args:
            major: major version
        Returns:
            minor version
        """
        minor = 0
        limit = 100  # Hard limit the search
        repo_url = f"https://repo.gardenlinux.io/gardenlinux/dists/{major}.{{}}/Release"

        while minor <= limit:
            try:
                check_url = repo_url.format(minor)
                response = requests.get(check_url)
                if response.status_code != 200:
                    # No more versions found, return last successful minor
                    return minor - 1
                minor += 1
            except requests.RequestException as e:
                self.log.debug(f"Error checking repo URL {check_url}: {e}")
                return minor - 1

        # If we hit the limit, return the last minor
        return minor - 1

    def get_version(self):
        """Get version using same logic as garden-version bash script.

        Args:
            version: version string
        Returns:
            version string
        """

        try:
            # Check VERSION file
            version_file = self.git_root / "VERSION"
            if version_file.exists():
                version = version_file.read_text().strip()
                # Remove comments and empty lines
                version = re.sub(r"#.*$", "", version, flags=re.MULTILINE)
                version = "\n".join(
                    line for line in version.splitlines() if line.strip()
                )
                version = version.strip()
            else:
                version = "today"

            if not version:
                version = "today"

            # Handle numeric versions (e.g., "27.1")
            if re.match(r"^[0-9\.]*$", version):
                major = version.split(".")[0]
                if int(major) < 10000000:  # Sanity check for major version
                    if "." in version:
                        return version  # Return full version if minor is specified
                    else:
                        # Get latest minor version from repo
                        minor = self.get_minor_from_repo(major)
                        return f"{major}.{minor}"

            # Handle 'today' or 'experimental'
            if version in ["today", "experimental"]:
                # Calculate days since start date
                start_timestamp = datetime.strptime(
                    self.start_date, "%b %d %H:%M:%S %Z %Y"
                ).timestamp()
                today_timestamp = datetime.now(timezone.utc).timestamp()
                major = int((today_timestamp - start_timestamp) / (24 * 60 * 60))
                return version

            # Handle date input
            try:
                # Try to parse as date
                input_date = datetime.strptime(version, "%Y%m%d")
                start_date = datetime.strptime(self.start_date, "%b %d %H:%M:%S %Z %Y")
                days_diff = (input_date - start_date).days
                return f"{days_diff}.0"
            except ValueError:
                pass

            return version

        except Exception as e:
            self.log.error(f"Error determining version: {e}")
            return "local"

    def get_short_commit(self):
        """Get short commit using same logic as the get_commit bash script.

        Returns:
            short commit string
        """
        try:
            # Check if COMMIT file exists in git root
            commit_file = self.git_root / "COMMIT"
            if commit_file.exists():
                return commit_file.read_text().strip()

            # Check if git repo is clean
            status_output = (
                subprocess.check_output(
                    ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL
                )
                .decode()
                .strip()
            )

            if status_output:
                self.log.info(f"git status:\n {status_output}")
                # Dirty repo or not a git repo
                return "local"
            else:
                # Clean repo - use git commit hash
                return (
                    subprocess.check_output(
                        ["git", "rev-parse", "--short", "HEAD"],
                        stderr=subprocess.DEVNULL,
                    )
                    .decode()
                    .strip()
                )

        except subprocess.CalledProcessError:
            return "local"

    def get_cname(self, platform, features, arch):
        """Get canonical name (cname) for Garden Linux image.

        Args:
            platform: Platform identifier (e.g., 'kvm', 'aws')
            features: List of features
            arch: Architecture ('amd64' or 'arm64')

        Returns:
            Generated cname string
        """
        # Get version and commit
        version = self.get_version()
        commit = self.get_short_commit()

        return f"{platform}-{features}-{arch}-{version}-{commit}"
