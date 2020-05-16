# A Cookiecutter for Python Internal Projects

**WARNING I** This won't work out of the box. It is meant as a starting point and source of (hopefully good) ideas for you. It contains a lot of assumptions based on my own internal requirements and restrictions. It is also not likely to be updated very often, so versions and some approaches will likely be obsolete by the time you look at this, but I still hope it can serve as a starting point and provides some ideas about how to deal with certain problems arising in an organisational context. I will try to keep it vaguely up to date with what I consider "good practices" for internal projects.

**WARNING II** I haven't double and triple checked everything here, as it is not really intended to work out of the box anyway, so there are likely some errors hidden here - let me know if you run into problems and I might be able to help.

There is a difference between private and public projects. The main differences are usually around versioning, package handling and deployment. In my courses I'm often asked how to deal with problems like that in an organisational context and I published this cookiecutter to have something that I can then loosely suggest without knowing any details about your specific setup.

So, if you think this is a good starting point: fork it into your organisation private repository hoster and adjust it, so it then can be used by internal teams to create new project templates. Locations where I already know for sure that they would need adjustments for your organisation are marked with "TODO adjust for your organisation". Also look for occurrences of "example.com" and check how you need to adjust this to your internal needs.

## How Does a Cookiecutter Work?

A cookiecutter takes a template like this one here and creates a new project from that using the users input to fill out what is needed as information for the new project.

If you don't have cookiecutter yet, you can install it like this: `pipx install cookiecutter` ([pip**x**](https://pipxproject.github.io/pipx/) - not pip).

Create a new project:

```text
# TODO adjust for your organisation
cookiecutter ssh://git@example.com/some-team/avira-ai-new-project.git
```

... and answer the questions (defaults are shown in square brackets) - a new
 directory using the project slug (`cool-new-project`) will be created in the current folder
 (or use `-o <foldername>`). You should not have to change any of the defaults as they can be derived from the project slug.

For more details about cookiecutter see their [great docs](https://cookiecutter.readthedocs.io).

## What Does it Do?

There are a lot of assumptions that might not fit your use case, but if you feel lost and need something to get started, this might still be helpful. Some assumptions are that you use git as version control, and internal PyPI mirror, and Bamboo for CI. Most of these should be adjustable with not too much effort though to your specific internal setup.

The cookiecutter creates a new project that ...

* is a valid Python package that can be published on a PyPI compatible package index (old skool - not PEP517/518 based)
* [tox](https://pypi.org/project/tox) based automation with environments for:
    * static code analysis and automatic fixes using [pre-commit](https://pypi.org/project/pre-commit/)
    * pytest based tests with coverage measurement using [coverage.py](https://pypi.org/project/coverage)
    * developing and publishing documentation (TODO open source bitbucket pages publisher)
    * checking requirements with [pip-checks-reqs](https://pypi.org/project/pip_check_reqs/)
* [editorconfig](https://editorconfig.org/) from the docs: "EditorConfig helps maintain consistent coding styles for multiple developers working on the same project across various editors and IDEs."
* check the project name if a valid importable name can be created from it to keep naming consistent (`hooks/pre_gen_project.py`) 
* Sphinx based documentation with todo links that contain the link to the file where the todo is located only when build locally (otherwise it contains the TODO without the then nonsensical file link)
* an automatic versioning mechanism (vendored script `versioneer.py`) 
    **NOTE** if your build system and other restrictions allow to work with VCS based automatic versioning, I would recommend to look into [setuptools-scm](https://pypi.org/project/setuptools-scm/) instead.
    * creates versions like:
        * dev: a timestamped versin that is always smaller than any production version
        * branch: 0.<issue number>.<build number> - is always smaller as any production version (>1.0) (e.g. 0.234.666). This is helpful if you have several packages that depend on each other and need to make changes in several of them. The requirements of the depending project can then be adjusted to depend on the newest build from that branch (via requesting `my-internal-dependency==0.<issue number>.*` in requirements.txt)
        * production: human controlled API part (in `VERSION_STUB`) plus automatically provided patch number (e.g. 2.0.239) - good enough for only internally used versioning  
    * please note that the vendored script `versioneer.py` is likely not suitable for your use case out of the box, but can serve as a starting point. Ideally it should also not be copy and pasted around but part of a suite of tools that are installed wherever packages need to be built, so on devboxes and CI systems.

**WARNING:** the publishing script for the documentation publishing is not included (yet - I might get around to open sourcing that at a later point). The basic idea there is the same as used e.g. by github pages: the documentation is built and committed into an orphan branch in the same repository that can then be hosted by the repository hoster. There are a few solutions out there that you might be able to use for this approach. Have a look at how e.g. [Lektor](https://www.getlektor.com/) or [mkdocs](https://www.mkdocs.org/) do this.

## Some More (Questionable?) Assumptions / Decisions

### Python 3.6

This is simply due to the fact that when I prepared this snapshot for publishing we are still using python3.6 ... I would recommend using the newest Python release though, whenever possible.

### No Source Folder (`src`)

The package is in the root of the project as it is traditionally the case in the majority of Python projects.

The idea behind adding a no-package `src` folder is to avoid accidentally testing the source code rather than the package with a packaging/testing tools like pytest and tox. The question whether this is a good idea or not is [strongly disputed](https://github.com/pypa/packaging.python.org/issues/320).
 
It turns out though that tox and pytest are not only the problem, they are also the solution if used correctly, making `src` unnecessary (at least in my limited experience with lost of organisation internal packages): 

1. during development tests are run against the develop install of the project and therefore there is no problem
2. the package is built and tested by tox and all we have to make sure there that the source code of the project can never be in `sys.path`, to do this we add a `changedir = {toxinidir}/tests` which assures this. 

This has a nice side effect: it is also a good way of assuring that tests are truly independent from which directory they are run, because they are then regularly run from the project root (usual place to run tests during development) and from the tests folder (tox).

### Simple Sphinx based documentation

Only absolutely necessary files are `index.rst` and `conf.py`

`_static` is where images and other static files got that also need to be deployed. If you add files you can remove `.gitkeep` (crutch as git does not track directories). If you are sure you never will have static files in the docs you can delete the folder and the corresponding setting in `conf.py`.  

`links.rst` is included in index and only contains the link to the project for now, but should be used for all reused links. If you don't need it, you can also get rid of it.

### What should be in `.gitignore`?

Only project specific and generally valid Python specific ignores should be in `.gitignore`, so this file has a representative collection with a hint that IDE and tool specific files that are not of the project should be in the users `~/.gitignore`.

### coverage.py

Measuring the test coverage as part of a normal test run. For simple projects this is sufficient. For more complex test suites usually several coverage data files need to be collected and consolidated as a last step. This is not covered here.
