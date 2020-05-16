"""Write package version during build or determine it during install.

In this vendored form, this must be a 3rd party dependency free, stand alone script.

WARNING: this should not be vendored in and contains a lot of assumptions that might
         not fit your use case.

Assumptions:
* branch names always start with the issue number
* you want to control the first two parts of the version and automate the third part
* You use a Bamboo build system (should be easily adjustable to other systems though)
"""
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

log = logging.getLogger(__name__)


def main():
    """Poor mans command line handling. This is stable and won't change (trust me)."""
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) == 1:
        raise ValueError("choose command: set or get")
    command = sys.argv[1]
    if command == "write_version_file":
        # called when the package is built
        write_version_file()
    elif command == "git-tag":
        # called as part of deploy to tag released versions
        assert command == "tag", f"bad command: {command}"
        git_tag()
    else:
        # called manually to remove bad tags
        assert command == "tag", f"bad command: {command}"
        git_remove_tag()


def write_version_file():
    """Write the version file for Bamboo and the package build.

    Try to fetch data from bamboo env, otherwise from commandline.
    """
    buildNumber = os.getenv("bamboo_buildNumber")
    branchName = os.getenv("bamboo_planRepository_branchName")
    if not buildNumber or not branchName:
        if os.getenv("bamboo_agentId"):
            bambooDict = {k: v for k, v in os.environ.items() if k.startswith("bamboo")}
            raise EnvironmentError(f"Bamboo environment incomplete: {bambooDict}")
    Versioneer.write_version_file(buildNumber=buildNumber, branchName=branchName)


def git_tag():
    """Tag a concrete hash with version number on release.

    Deliberately ugly, because I don't know what I am doing.
    url = "ssh://git@your-code-repo/..."
    """
    # FIXME just written down - not tested yet
    gitHash, version, url = sys.argv[1:]
    with tempfile.TemporaryDirectory() as tmpPath:
        log.info(f"cloning {url} to {tmpPath}")
        subprocess.check_call(["git", "clone", url, tmpPath])
        oldCwd = Path.cwd()
        try:
            os.chdir(tmpPath)
            log.info(f"tagging {gitHash} with {version}")
            subprocess.check_call(["git", "pull"])
            subprocess.check_call(["git", "tag", "-f", version, gitHash])
            subprocess.check_call(["git", "push", "-f", "origin", version])
        finally:
            os.chdir(str(oldCwd))


def git_remove_tag():
    """Remove version tag from repo, to correct errors.

    Deliberately ugly, because I don't know what I am doing yet.
    """
    version = sys.argv[1]
    try:
        subprocess.check_call(["git", "tag", "-d", version])
    except subprocess.CalledProcessError:
        pass
    subprocess.check_call(["git", "push", "origin", ":refs/tags/{}".format(version)])


class Versioneer:
    VERSION_STUB_PATH = Path("VERSION_STUB")
    """Contains <major>.<minor> for projects in production.

    Used to construct the version from an API part and an ever incrementing buildnumber.
    """
    VERSION_FILE_PATH = Path("VERSION")
    """Contains version=<major>.<minor>.<bamboo build number> for production builds.

    Used to determine the version during installation.
    """
    BAMBOO_VERSION_VAR_PREFIX = "version="
    """See inject variables plugin for bamboo: https://bit.ly/2kec2df"""
    SPECIAL_MAJOR = "0"
    """Marks local build, branch builds and projects without VERSION_STUB."""
    LOCAL_MINOR = "1"
    """marks local builds (and project without VERSION_STUB)"""
    VERSION_STUB_PATTERN = re.compile(r"^[\d]+\.[\d]+$")

    @classmethod
    def write_version_file(cls, *, buildNumber, branchName):
        """write a VERSION file in the root of the project.

        Used as part of the build process.

        Integration into Bamboo:
            * Add an inject variables task in Bamboo with configuration:
                * path to properties file: ``<project root>/VERSION``
                * namespace: dontcare (arbitrary namespace)
                * Scope: result (so it is also available in deployment project)

        Example from bamboo build log that shows that it works:
            <date> Injected variable bamboo.dontcare.version=1.0.114 in RESULT scope

        Version is then accessible in deployment as ${bamboo.dontcare.version}

        NOTE: version file format is bamboo requirement: https://goo.gl/Maek4N)
        """
        try:
            versionStub = cls.VERSION_STUB_PATH.read_text().strip()
        except IOError:
            versionStub = f"{cls.SPECIAL_MAJOR}.{cls.LOCAL_MINOR}"
        assert cls._is_valid(versionStub), f"invalid stub: {versionStub}"
        cwd = Path.cwd()
        assert (cwd / "setup.py").exists(), f"not project root or not setup.py ({cwd})"
        version = cls._make_version(versionStub, buildNumber, branchName)
        text = f"{cls.BAMBOO_VERSION_VAR_PREFIX}{version}"
        cls.VERSION_FILE_PATH.write_text(text)
        log.info(f"written '{text}' to {cls.VERSION_FILE_PATH}")

    @classmethod
    def _make_version(cls, versionStub, buildNumber, branchName):
        if branchName == "master":
            assert buildNumber, f"{versionStub}, {buildNumber}, {branchName}"
            return f"{versionStub}.{buildNumber}"
        minor = cls._get_issue_number(branchName)
        if minor:
            return f"{cls.SPECIAL_MAJOR}.{minor}.{buildNumber}"
        return cls._make_unique_dev_version()

    @classmethod
    def _make_unique_dev_version(cls):
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        return f"{cls.SPECIAL_MAJOR}.{cls.LOCAL_MINOR}.{timestamp}"

    @classmethod
    def _get_issue_number(cls, branchName):
        if branchName:
            try:
                return re.match(r"(\d+).*", branchName).group(1)
            except AttributeError:
                return None

    @classmethod
    def _is_valid(cls, stub):
        return cls.VERSION_STUB_PATTERN.match(stub) is not None


if __name__ == "__main__":
    main()
