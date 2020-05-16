"""https://packaging.python.org/"""
import subprocess
from pathlib import Path

from setuptools import setup, find_packages

HERE = Path(__file__).parent.resolve()  # resolve necessary in pip build context


def get_version():
    def read_from_file(must_exist):
        # install or build after file was written (must exist then).
        version_path = HERE / "VERSION"
        if version_path.exists():
            return version_path.read_text().strip().replace("version=", "")
        if must_exist:
            raise EnvironmentError(f"need {version_path}")

    version = read_from_file(must_exist=False)
    if version:
        return version
    # build: make version, write it for Bamboo and install, return for pkg file name.
    versioneer_path = HERE / "versioneer.py"
    subprocess.check_call(["python3.6", str(versioneer_path), "write_version_file"])
    return read_from_file(must_exist=True)


kwargs = dict(
    name="{{ cookiecutter.project_slug }}",
    version=get_version(),
    packages=find_packages(exclude=["docs", "tests"]),
    # TODO adjust for your organisation
    author="Example Organisation",
    # TODO adjust for your organisation
    author_email="some-team@example.com",
    install_requires=(HERE / "requirements.txt").read_text(),
    extras_require={"test": (HERE / "requirements-test.txt").read_text()},
    # If you need command line executables ...
    # entry_points={"console_scripts": ["executable-name = path.to.module:function"]},
    url="{{ cookiecutter.project_url }}",
)


if __name__ == "__main__":
    setup(**kwargs)
