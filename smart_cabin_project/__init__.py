import os
# Extend the package path so that imports of `smart_cabin_project` resolve to the inner project directory.
__path__.append(os.path.join(os.path.dirname(__file__), "smart_cabin_project"))