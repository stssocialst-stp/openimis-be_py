import os
import logging
from importlib import resources

from .openimisconf import load_openimis_conf

logger = logging.getLogger(__name__)


def extract_app(module):
    return "%s" % (module["name"])


def openimis_apps():
    OPENIMIS_CONF = load_openimis_conf()
    apps = [*map(extract_app, OPENIMIS_CONF["modules"])]

    # Add PEP+ module dynamically if it exists (for development)
    if os.path.exists('/app/openimis-be-pep_plus_py') and 'pep_plus' not in apps:
        apps.append('pep_plus')

    return apps


def get_locale_folders():
    """
    Get locale folders for the modules in a reverse order to make it easy to override the translations
    """
    apps = []
    basedirs = []
    seen_paths = set()  # Track seen paths to avoid duplicates

    for mod in load_openimis_conf()["modules"]:
        mod_name = mod["name"]
        try:
            with resources.path(mod_name, "__init__.py") as path:
                apps.append(path.parent.parent)
        except ModuleNotFoundError:
            raise logger.error(f"Module \"{mod_name}\" not found.")

    for topdir in ["."] + apps:
        for dirpath, dirnames, filenames in os.walk(topdir, topdown=True):
            for dirname in dirnames:
                if dirname == "locale":
                    locale_path = os.path.join(dirpath, dirname)
                    # Only add if not already in the list (avoid duplicates)
                    if locale_path not in seen_paths:
                        basedirs.insert(0, locale_path)
                        seen_paths.add(locale_path)
    return basedirs
