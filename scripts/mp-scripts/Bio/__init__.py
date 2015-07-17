# Copyright 2000 by Jeffrey Chang.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.
"""Collection of modules for dealing with biological data in Python.

The Biopython Project is an international association of developers 
of freely available Python tools for computational molecular biology.

http://biopython.org
"""

class MissingExternalDependencyError(Exception):
    pass

def _load_registries():
    import sys, os
    from Bio.config.Registry import Registry
    
    if getattr(sys, "version_info", (1, 5))[:2] < (2, 1):
        return

    self = sys.modules[__name__]        # self refers to this module.
    # Load the registries.  Look in all the '.py' files in Bio.config
    # for Registry objects.  Save them all into the local namespace.
    # Import code changed to allow for compilation with py2exe from distutils
    # import Bio.config
    config_imports = __import__("Bio.config", {}, {}, ["Bio"])
    # in a zipfile
    if hasattr(config_imports, '__loader__'):
        zipfiles = __import__("Bio.config", {}, {}, ["Bio"]).__loader__._files
        # Get only Bio.config modules
        x = [zipfiles[file][0] for file in zipfiles.keys() \
                if 'Bio\\config' in file]
        x = [name.split("\\")[-1] for name in x] # Get module name
        x = map(lambda x: x[:-4], x) # chop off '.pyc'
    # not in a zipfile, get files normally
    else:
        x = os.listdir(os.path.dirname(config_imports.__file__))
        x = filter(lambda x: not x.startswith("_") and x.endswith(".py"), x)
        x = map(lambda x: x[:-3], x)            # chop off '.py'
    for module in x:
        module = __import__("Bio.config.%s" % module, {}, {}, ["Bio","config"])
        for name, obj in module.__dict__.items():
            if name.startswith("_") or not isinstance(obj, Registry):
                continue
            setattr(self, name, obj)

# Put the registry loading code in a function so we don't polute the
# module namespace with local variables.

# WARNING:
# The call to _load_registries is being skipped as part of deprecating
# Bio.expressions, which does not function properly with the new version
# of mxTextTools. If at some point we decide to revive Bio.expressions,
# this line should be reinstated.

# _load_registries()


del _load_registries
