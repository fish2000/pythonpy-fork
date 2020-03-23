py -c '
import os
import pkg_resources
print(os.path.abspath(pkg_resources.resource_filename("pythonpy.completion", "pycompletion.sh")))
'
