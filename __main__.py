# __main__.py
# Stephen McDowell, April 2017
# Walker White, November 2012

# [[[ BEGIN_MAIN_PY_DOC ]]]
'''
The ``__main__`` module for MacPan

This is the module with the script code to start up the App.  Make
sure that this module is in a folder with the following files:

+-------------------+-------------------------------+
| File              | Purpose                       |
+===================+===============================+
| ``controller.py`` | The primary controller class. |
+-------------------+-------------------------------+
| ``model.py``      | The model classes.            |
+-------------------+-------------------------------+
| ``view``          | Directory with view classes.  |
+-------------------+-------------------------------+



Moving any of these folders or files will prevent the game from
working properly. You are free to add new files into these
folders as you wish.
'''
# [[[ END_MAIN_PY_DOC ]]]

import sys
import os

try:
    from PyQt4 import QtGui
except:
    # The error_out module exits the application with a message to indicate how to fix
    # the problem.  It's complex enough that we moved it to it's own file, but this is
    # generally speaking a "strange" thing to do in Python!
    from error_out import notify_course_of_action
    sys.exit(notify_course_of_action())

# When running the folder, we do not actually "import".  This makes it so that the files
# throughout the rest of the framework can perform "regular" imports.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
try:
    from view.qt_configs import qdarkstyle
    from view.display import CitizenPacMainWindow
    from controller import CitizenPac
except Exception as e:
    sys.stderr.write("Unable to perform all imports: {}\n".format(e))
    sys.exit(1)


def main():
    """
    PyQt does not delete objects in the right order reliably, occasionally it can raise
    a segmentation fault (among other errors) upon exit of the program.

    By placing everything in a self contained method and calling that from below in the
    ``if __name__ == "__main__"`` block, we force that this method completes execution
    and bypass this problem.
    """
    ####################################################################################
    # Is the game running slowly?  Un-comment the line below this.                     #
    # QtGui.QApplication.setGraphicsSystem("raster")                                   #
    ####################################################################################
    app = QtGui.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))

    cpMainWindow = CitizenPacMainWindow()
    controller = CitizenPac(app, cpMainWindow)  # noqa F841

    cpMainWindow.show()
    cpMainWindow.raise_()
    # cpMainWindow.setActiveWindow()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
