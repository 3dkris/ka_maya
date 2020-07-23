#====================================================================================
#====================================================================================
#
# reloadPackage
#
# DESCRIPTION:
#   reloads all modules in ka_irs
#
# AUTHOR:
#   Kris Andrews (3dkris@3dkris.com)
#
#====================================================================================
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:

    #(1) Redistributions of source code must retain the above copyright
    #notice, this list of conditions and the following disclaimer.

    #(2) Redistributions in binary form must reproduce the above copyright
    #notice, this list of conditions and the following disclaimer in
    #the documentation and/or other materials provided with the
    #distribution.

    #(3)The name of the author may not be used to
    #endorse or promote products derived from this software without
    #specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
#IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
#INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#POSSIBILITY OF SUCH DAMAGE.
#====================================================================================


PACKAGE_RELOADERS = []
MODULES = []
add = MODULES.append

# PYTHON PACKAGE_RELOADERS (IN ORDER) ##########################################
import ka_maya.reload_package; PACKAGE_RELOADERS.append(ka_maya.reload_package)

# PYTHON MODULES (IN ORDER) ####################################################
import ka_maya_local.core as core                                               ;add(core)
import ka_maya_local.menus as menus                                             ;add(menus)


def reload_package():
    """Call this function to reload package"""
    for package_reloader in PACKAGE_RELOADERS:
        reload(package_reloader)
        package_reloader.reload_package()

    message = '>> Reloading KA_MAYA_LOCAL'
    print message, '='*(80-len(message))

    for module in MODULES:
        reload(module)

def get_previous_modified_time():
    previous_modified_time = 0
    for module in MODULES:
        modified_time = os.stat(module.__file__)[8]
        if modified_time > previous_modified_time:
            previous_modified_time = modified_time
    return previous_modified_time


def has_changed(previous_modified_time):
    result = False
    for module in MODULES:
        modified_time = os.stat(module.__file__)[8]
        result = result or ( modified_date <= previous_lastest_change )
    return result