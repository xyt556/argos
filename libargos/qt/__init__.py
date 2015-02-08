# -*- coding: utf-8 -*-

# This file is part of Argos.
# 
# Argos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Argos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Argos. If not, see <http://www.gnu.org/licenses/>.

""" Qt specific stuff, which is not specific to this project.
"""

# Abstracts away the differences between PySide and PyQt
USE_PYQT = False # PySide is used when False

if USE_PYQT:
    # This is only needed for Python v2 but is harmless for Python v3.
    import sip
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QString', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)
    

if USE_PYQT:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtCore import Qt
    from PyQt4.QtCore import pyqtSignal as QtSignal
    from PyQt4.QtCore import pyqtSlot as QtSlot_Unchecked 
else:
    from PySide import QtCore, QtGui
    from PySide.QtCore import Qt
    from PySide.QtCore import Signal as QtSignal
    from PySide.QtCore import Slot as QtSlot_Unchecked

QtSlot = QtSlot_Unchecked


import sys, logging, traceback

from .. import info
from libargos.utils.cls import check_class

logger = logging.getLogger(__name__)


def printChildren(obj, indent=""):
    """ Recursively prints the children of a QObject. Useful for debugging.
    """
    children=obj.children()
    if children==None:
        return
    for child in children:
        try:
            childName = child.name()
        except AttributeError:
            childName = "<no-name>"
            
        print ("{}{:10s}: {}".format(indent, childName, child.__class__))
        printChildren(child, indent + "  ")


def __check_slot_function_result(f):
    """ Aux function that wraps QtSlot in a function that halts in case of an exception
    """
    def check_slot_function_result_wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if result is not None:
                raise ValueError("Value returned from slot function '{}' is not None, but '{!r}'"
                                 .format(f, result))
        except BaseException as ex:
            logger.exception("Bug: unexpected exception: {}".format(ex))
            if info.DEBUGGING:
                sys.exit(1)
            else:
                msgBox = QtGui.QMessageBox()
                msgBox.setText("Bug: unexpected {}".format(type(ex).__name__))
                msgBox.setInformativeText(str(ex))
                msgBox.setDetailedText(str(traceback.format_exc()))
                msgBox.setIcon(QtGui.QMessageBox.Warning)
                msgBox.exec_()
                
        return None # this is what a slot expects
    return check_slot_function_result_wrapper


#if USE_PYQT:
#    logger.warn("Checked slots don't work yet with PyQt")
#    QtSlot = QtSlot_Unchecked
#else:        
#    def QtSlot(*args, **kwargs):
#        """ A QT slot decorator that will cause the program to exit in case of an exception
#            or in case the slot doesn't return None
#        """
#        decorator = QtSlot_Unchecked(*args, **kwargs)
#        def wrapped_qtslot_decorator(f):
#            logger.debug("Wrapping: {!r}".format(f))
#            return decorator(__check_slot_function_result(f))
#        return wrapped_qtslot_decorator



def getQApplicationInstance():
    """ Returns the QApplication instance. Creates one if it doesn't exist.
    """
    app = QtGui.QApplication.instance()

    if app is None:
        app = QtGui.QApplication(sys.argv)
    check_class(app, QtGui.QApplication)
    
    app.setApplicationName(info.REPO_NAME)
    app.setApplicationVersion(info.VERSION)
    app.setOrganizationName(info.ORGANIZATION_NAME)
    app.setOrganizationDomain(info.ORGANIZATION_DOMAIN)    
    
    return app



def handleException(exc_type, exc_value, exc_traceback):

    traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    logger.error("Bug: unexpected {}".format(exc_type), 
                 exc_info=(exc_type, exc_value, exc_traceback))
    if info.DEBUGGING:
        sys.exit(1)
    else:
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Bug: unexpected {}".format(exc_type.__name__))
        msgBox.setInformativeText(str(exc_value))
        lst = traceback.format_exception(exc_type, exc_value, exc_traceback)
        msgBox.setDetailedText("".join(lst))
        msgBox.setIcon(QtGui.QMessageBox.Warning)
        msgBox.exec_()
        sys.exit(1)
                
# Must be after application instance has been instantiated
sys.excepthook = handleException
