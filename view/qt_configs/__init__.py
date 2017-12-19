'''
This sub-package exists to hide away some of the more grungy details of how ``PyQt4``
works, including its resource system and UI Design framework.

.. danger::

   Do not edit anything under this directory **while you are working on the assignment**.
   If you make changes, these changes could potentially break the entire framework,
   which is why it is separated out into its own little sub-directory.

   What follows is what you could do to change things, **after** you have finished
   the assignment.

.. tip::

   If you make changes here that break everything, and cannot figure out what the
   problem was, simply download the release code and replace this directory!

QtConfigs HowTo
========================================================================================

There are a few different things going on with this directory, the primary motivation
being to avoid students needing to install anything on their own. Qt provides a few
different mechanisms for creating "resources", GUIs, and linking them all together.

Additionally, to avoid students needing to ``conda install`` anything, we are providing
them with a copy of the
`qdarkstyle <https://github.com/ColinDuquesnoy/QDarkStyleSheet>`__ repository,
including its top-level README and license (``COPYING``). Some of the elements of the
repository have been removed (e.g. the examples), to reduce the number of files students
need to receive.

Qt Resources
----------------------------------------------------------------------------------------

Qt uses an xml-like `resource system <http://doc.qt.io/qt-4.8/resources.html>`__ to
manage locating files within an application. It is generally pretty straightforward to
setup, the key difference here being that the ``.qrc`` (Qt resource file) is
traditionally stored in the top-level directory. To accommodate that we are **two**
directories below, the resource document is structured as follows:

.. code-block:: xml

    <!DOCTYPE RCC>
        <RCC version="1.0">
        <qresource prefix="/view/qt_configs">
            ...
        </qresource>
    </RCC>

This enables us to still gain access to the resources we need when executing from the
top-level ``citizen_pac/__main__.py`` file, i.e. when running ``python citizen_pac``.

**Before** this file can be used, though, we must enable the resources to be acquired
via the ``PyQt`` interface. The tool to do this is called ``pyrcc4``, and is vendored
with the Anaconda installation. Please be aware that the GUI uses this resource file as
well, and decisions made in this portion must agree with the decisions made for
converting the UI toolkit (next section). Since the datatypes for ``str`` have changed
between Python2 and Python3, be aware that if this assignment is used again in the
future (i.e. after 1110 switches to Python3), you will need to create the appropriate
binding.

Assuming you are in the same directory as ``citizen_pac.qrc``, execute the following:

.. code-block:: console

    $ pyrcc4 -py2 -o citizen_pac_rc.py citizen_pac.qrc

Breakdown
****************************************************************************************

``-py2``
    Create the Python2 resources. Use ``-py3`` for Python3!

``-o citizen_pac_rc.py``
    The file to save the embedded resources in.  The ``ui`` tool in the next section
    defaults to looking for ``_rc.py``, advise keeping this the same.

``citizen_pac.qrc``
    The resource file to convert.

You now have the relevant python module that will be imported by the UI toolkit.

Qt UI Toolit
----------------------------------------------------------------------------------------

Included in your installation of Anaconda should be an executable ``designer-qt4`` (it
will be ``-qt5`` in the future, since Anaconda has now switched to Qt5). This is their
WYSIWYG gui editor. The UI file that was created by this program for use with this
assignment is ``citizen_pac.ui``. To launch the editor / make changes:

.. code-block:: console

    $ designer-qt4 citizen_pac.ui

Take note that this ``ui`` file already has the ``citizen_pac.qrc`` resource file linked
in as its main resource file. This **is** important -- the ``icon`` for the main window
is described by the resource file!

Like the resource file, in order to use this in Pythin via ``PyQt``, we need to use the
tool vendored by Qt to convert the ``ui`` file into something Python can work with. The
tool is called ``pyuic4``, and a helpful feature they have is to be able to preview
(using the ``-p`` flag) what it will look like:

.. code-block:: console

    $ pyuic4 -p citizen_pac.ui

When you are satisfied with the output (either via the preview, or from the editor), you
will need to use this tool to convert it to a Python module.

.. code-block:: console

    $ pyuic4 -o qt_generated_ui.py citizen_pac.ui

Breakdown
****************************************************************************************

``-w``
    Creates a class that inherits from the generated UI *and* ``QtGui.QMainWindow``.
    Unless you rename things in the ``citizen_pac.ui`` file, the class should be named
    exactly ``CitizenPacMainWindow``. This comes from the title of the root component
    ``QMainWindow`` in the editor. The class generated at the bottom is a convenience
    function, noting that the ``import citizen_pac_rc`` is what was mentioned previously
    -- the resource file name is important. You can use the ``--resource-suffix`` to
    change this.

    .. code-block:: py

       import citizen_pac_rc

       class CitizenPacMainWindow(QtGui.QMainWindow, Ui_CitizenPacMainWindow):
           def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
               QtGui.QMainWindow.__init__(self, parent, f)

               self.setupUi(self)

    Technically you do not need to use this, you can instead use the
    ``Ui_CitizenPacMainWindow`` directly in the rest of the framework. But if you look
    at the arcane nature by which the class is initializing its members...if you ever
    forget to call the ``self.setupUi(self)`` method you will be sad. So I strongly
    advise you just inherit from ``CitizenPacMainWindow`` like is done currently to
    avoid forgetting this!

``-o QtGeneratedUI.py``
    The name of the resultant python module. If you change the name of this file, you
    will need to update the ``import`` statements elsewhere in the framework.

``citizen_pac.ui``
    The input ``ui`` file to be converted.

QDarkStyleSheet
----------------------------------------------------------------------------------------

Colin Duquesnoy, the author, is kind enough to maintain his project with an MIT license.
Though there is probably a way to link this in directly with the Qt resource system, I
didn't find it to be worth my time. Instead, we hide the repository down here so that
students can happily be oblivious to its existence, but do not need to install it
themselves. The stylesheet is used in ``__main__.py`` right after the ``app`` is
created.

See Colin's `instructions for use with PySide / PyQt4 /
PyQt5 <https://github.com/ColinDuquesnoy/QDarkStyleSheet#usage>`__, if you use this
assignment in the future you will almost certainly be using ``PyQt5`` and will therefore
need to make a small update to the ``__main__.py`` to initialize the stylesheet
correctly.

While you are at it, you will probably want to grab the latest stable version from his
repository. For reference, the version of the library that came with this release is
version 2.2, released on June 19th 2016.

All I did was download the source tarball, move the ``README.md`` and ``COPYING`` files
into the ``qdarkstyle`` subdirectory (that's the actual python package), move the
``qdarkstyle`` folder to this directory and delete the rest. E.g.

.. code-block:: console

    # Download and extract the current release (click on releases tab on GitHub)
    $ wget https://github.com/ColinDuquesnoy/QDarkStyleSheet/archive/2.2.tar.gz
    $ tar -xf 2.2.tar.gz

    # Enter extracted directory and reorganize
    $ cd QDarkStyleSheet-2.2/
    $ mv README.md qdarkstyle/
    $ mv COPYING qdarkstyle/
    # Not necessary, but no reason to keep
    $ rm qdarkstyle/.gitignore

    # Now that the README and license are in `qdarkstyle`
    # move that above so we can distribute and delete
    # the extra items from the repo we do not need
    $ mv qdarkstyle/ ..
    $ cd ..
    $ rm -rf QDarkStyleSheet-2.2/
    $ rm 2.2.tar.gz

No matter what, **make sure you distribute the license with this folder**!
'''

from qt_generated_ui import Ui_CitizenPacMainWindow


# Typically packagers will ``import`` all modules from their library in the ``__init__``
# file, but the author of ``qdarkstyle`` does not have this freedom.  The library is
# written to conditionally include modules depending on whether ``PySide``, ``PyQt4``,
# or ``PyQt5`` are being used.  As such, we need to make the modules that ``qdarkstyle``
# will need available in our system path.
import qdarkstyle
import sys
import os
sys.path.insert(1, os.path.abspath(os.path.dirname(__file__)))

__all__ = ["Ui_CitizenPacMainWindow", "qdarkstyle"]
