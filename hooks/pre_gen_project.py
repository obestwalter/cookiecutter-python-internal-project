import re
import sys

NAME_REGEX = r'^[\-a-z][\-a-z0-9]+$'
project_slug = '{{ cookiecutter.project_slug}}'
if not re.match(NAME_REGEX, project_slug):
    sys.exit(
        "USER ERROR: "
        f"The project slug must adhere to the regex '{NAME_REGEX}' to translate "
        f"into a valid module name. Use what would be a valid Python module name "
        f"but use '-' instead of '_' (e.g. some-good-project-name).\n"
        f"Do only use lower case ASCII letters.\n"
        f"Do not use underscores in the name - use dashes.\n"
    )
