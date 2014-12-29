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

""" Repository items (RTIs) for browsing the file system
"""

import logging, os
from .treeitems import (ICONS_DIRECTORY, BaseRti)
from libargos.qt import QtGui

logger = logging.getLogger(__name__)


_ICOLOR = '666666' # icons in dark gray


class UnknownFileRti(BaseRti):
    """ A repository tree item that has a reference to a file of unknown type. 
        The file is not opened.
    """
    _iconOpen = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'file.{}.svg'.format(_ICOLOR)))
    _iconClosed = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'file-inverse.{}.svg'.format(_ICOLOR)))    
    
    def __init__(self, nodeName='', fileName=''):
        """ Constructor 
        """
        BaseRti.__init__(self, nodeName=nodeName, fileName=fileName)
        assert os.path.isfile(self.fileName), "Not a regular file: {}".format(self.fileName)

    def hasChildren(self):
        """ Returns False. Leaf nodes never have children. """
        return False
    

class DirectoryRti(BaseRti):
    """ A repository tree item that has a reference to a file. 
    """
    _iconOpen = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'folder-open.{}.svg'.format(_ICOLOR)))
    _iconClosed = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'folder-close.{}.svg'.format(_ICOLOR)))
    
    def __init__(self, nodeName='', fileName=''):
        """ Constructor
        """
        BaseRti.__init__(self, nodeName=nodeName, fileName=fileName)
        if fileName:
            assert os.path.isdir(fileName), \
                "Not a directory: {!r} {!r}".format(self.fileName, fileName)

        
    @property
    def icon(self):
        "Icon displayed"
        if self._childrenFetched:
            return self._iconOpen
        else:
            return self._iconClosed
        
        
    def _fetchAllChildren(self):
        """ Gets all sub directories and files within the current directory.
            Does not fetch hidden files.
        """
        childItems = []
        fileNames = os.listdir(self._fileName)
        absFileNames = [os.path.join(self._fileName, fn) for fn in fileNames]

        # Add subdirectories
        for fileName, absFileName in zip(fileNames, absFileNames):
            if os.path.isdir(absFileName) and not fileName.startswith('.'):
                childItems.append(DirectoryRti(fileName=absFileName, nodeName=fileName))
            
        # Add regular files
        for fileName, absFileName in zip(fileNames, absFileNames):
            if os.path.isfile(absFileName) and not fileName.startswith('.'):
                childItems.append(UnknownFileRti(fileName=absFileName, nodeName=fileName))
                        
        return childItems
    
    