"""
This module provides one method (:func:`notify_course_of_action`), which serves to
give a slightly more helpful error message when a student tries to complete this
assignment with an incompatible version of Python installed.

Often times in the wild you will encounter long and complicated ``__main__.py`` (as
well as more often, long and complicated ``__init__.py`` files).  We were concerned
about students being able to run the assignment, but did not want to detract from what
``__main__.py`` was actually doing.  That is, the core mechanics of ``__main__.py``
are relatively straightforward:

1. Import the relevant utilities from the modules in the assignment.
2. Run the main method.

However, it seemed likely that some students may not have had the right version of
Anaconda Python.  Depending on when you installed it, there were certain crucial updates
related to the core library we used for displaying the assignment.  We elected to
separate this out into a different file so that when you read ``__main__.py`` you would
be able to see more clearly what it is doing.

In short, this is a long way of saying the use of ``error_out.py`` is non-standard, and
only exists due to the circumstances surrounding this particular assignment's code-base.
"""

import sys
import re
import textwrap


def notify_course_of_action():
    '''
    This method checks to see what version of python is installed, and informs the user
    where to go to get the correct version of python for this semester.

    If this code-base is used in the future, the default library will be ``PyQt5``, so

    1. Switch the imports for ``PyQt4`` from ``__main__.py`` and ``PyQt5`` from below.
    2. Update the ``semester`` variable, and ``install_base`` if the website layout
       has changed to a new setup.
    3. Update the ``anaconda_needs`` variable for the correct version.

    Refer to the `PyQt documentation`_ for more information on switching to ``PyQt5``.

    .. _PyQt documentation: http://pyqt.sourceforge.net/Docs/PyQt5/pyqt4_differences.html

    :Return:
        ``int``
            Always returns ``1`` (indicates error).
            Intended use: ``sys.exit(notify_course_of_action())``.
    '''
    # Generate an error message to guide what the problem is.
    website_base         = "https://www.cs.cornell.edu/courses/cs1110"
    semester             = "2017sp"
    install_base         = "materials/python.php#install"
    install_instructions = "{}/{}/{}".format(website_base, semester, install_base)

    # The Anaconda we installed at the beginning of the semester should have been 4.1.1
    # but starting with 4.2.0, PyQt5 was vendored instead.  Hopefully no students actually
    # hit this code, but better to try and give as much information as possible.
    anaconda_needs = "4.1.1"
    anaconda_match = re.match(r".*\|Anaconda (\d\.\d\.\d).*\|.*", sys.version)
    if anaconda_match:
        anaconda_version = anaconda_match.groups()[0]
    else:
        anaconda_version = "No Anaconda python detected!"

    # If they installed a newer version of Anaconda, PyQt4 and PyQt5 are not compatible
    # and cannot be used interchangeably.  They should be very similar, but the author
    # of this file does not have time to discover any such bugs.  What is evident is
    # that the import paths have changed.
    #
    # Excellent documentation for potential forward port here:
    #
    #     http://pyqt.sourceforge.net/Docs/PyQt5/pyqt4_differences.html
    #
    # You may get lucky, and just have to change imports?
    err_msg_front = "There seems to be an issue with the version of python you have " \
                    "installed.  Please make sure you have the correct version of "   \
                    "Anaconda python for *THIS* semester ({0}), instructions can be " \
                    "found here:".format(semester)
    err_msg_expects = "The version of Anaconda python expected"
    err_msg_located = "The version of Anaconda python we found"

    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication([])  # noqa: F841
        err_msg = textwrap.dedent('''
            {0}

                <a href="{1}">{1}</a>

            {2}: <b>{3}</b>
            {4}: <b>{5}</b>
        '''.format(err_msg_front, install_instructions,
                   err_msg_expects, anaconda_needs,
                   err_msg_located, anaconda_version))
        QMessageBox.critical(None, "MacPan", err_msg.replace("\n", "<br />"))
    except:
        # Same error message as before, just don't use the html formatting since this
        # is getting sent to the console.
        err_msg = textwrap.dedent('''
            {0}

                {1}

            {2}: {3}
            {4}: {5}
        '''.format(err_msg_front, install_instructions,
                   err_msg_expects, anaconda_needs,
                   err_msg_located, anaconda_version))

        sys.stderr.write(err_msg)

    return 1
