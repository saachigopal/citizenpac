'''
The Controller in the Model-View-Controller paradigm.
'''

# FILE VERSION: released 5/5/2017 @ 13:00

from PyQt4 import QtCore, QtGui

import constants
from model import Scene
from view.display import GameStats


class LostFocusFilter(QtCore.QObject):
    '''
    A simple filter to signal to the Controller that the moving flags of the CitizenPac
    actor needs to be reset.  Without this filter, if you hold one of the directional
    keys ``w``, ``a``, ``s``, or ``d`` and then move focus away from the application
    (e.g. sloppy mouse focus, or ``alt`` + ``tab``), the CitizenPac actor would continue
    moving on its own because the key released event is never received.  This filter
    simply detects when the focus is no longer on the game, and signals to the
    Controller, which in turn resets the CitizenPac actor.

    :Attributes:
        ``controller`` (:class:`controller.CitizenPac`)
            The Controller instance to signal when the application has lost focus.
    '''
    def __init__(self, controller, parent=None):
        super(LostFocusFilter, self).__init__(parent)
        self.controller = controller

    def eventFilter(self, obj, event):
        '''
        An event filter to signal to the Controller that the application has lost focus.
        The event issued is ``ApplicationDeactivate`` from the
        :class:`PyQt4.QtCore.QEvent` class, upon detection the
        :func:`controller.CitizenPac.appLostFocus()` method is called.

        :Parameters:
            ``obj`` (:class:`PyQt4.QtCore.QObject`)
                The object that signaled the event.  Irrelevant for the purposes of this
                method since we always want to handle this event regardless of where it
                came from.

            ``event`` (:class:`PyQt4.QtCore.QEvent`)
                The event that needs to be checked for filtering.

        :Return:
            ``bool``
                ``True`` if the event is being handled (prevents propagation to the rest
                of the objects), ``False`` if not handled.  For this filter, the return
                will be ``True`` if and only if
                ``event.type() == QtCore.QEvent.ApplicationDeactivate``.
        '''
        if event.type() == QtCore.QEvent.ApplicationDeactivate:
            self.controller.appLostFocus()
            return True

        return False


class CitizenPac(object):
    '''
    The main controller.  This class is responsible for creating, configuring, and
    driving the Model and View portions of the Model-View-Controller paradigm.

    :Parameters:

        ``app`` (:class:`PyQt4.QtGui.QApplication`)
            The main QtApplication instance, instantiated in ``__main__.py``.

        ``cpMainWindow`` (:class:`view.display.CitizenPacMainWindow`)
            The main window associated with this game.  Must be created **after** the
            ``app`` (Qt internally associates them).

            .. danger::

                The names of the widgets in the ``view/qt_configs/citizen_pac.ui``
                design file are exceptionally important.  The name of each widget causes
                the UI Converter to name the attributes of the class it generates based
                off these labels, and the names are hard-coded in this file.  In short:
                **do not rename widgets without updating this file!**

    :Attributes:

        **Qt Wrappers**
            ``app`` (:class:`PyQt4.QtGui.QApplication`)
                Reference to the main application.  It is only stored so that we can
                install the :class:`controller.LostFocusFilter` event filter.

            ``cpMainWindow`` (:class:`view.display.CitizenPacMainWindow`)
                The UI generated wrapper class that represents the Game GUI Layout.

        **State Variables**
            ``gameRunning`` (bool)
                Whether or not the game is currently running.

            ``gameFinished`` (bool)
                Whether or not the game has been completed (all food consumed, or have
                run out of lives).

            ``livesLeft`` (int)
                The number of lives left.

            ``speedIncr`` (float)
                The game speed increment for the given game.  Refer to the documentation
                for :data:`constants.USE_SPEED_BOOST`.

        **Mechanics Variables**
            ``view`` (:class:`PyQt4.QtGui.QGraphicsView`)
                The View portion of the Model-View-Controller paradigm.  Also a
                convenience rename of ``self.cpMainWindow.citizenPacGraphicsView`` as
                was named by the Ui generator from PyQt.

            ``scene`` (:class:`model.Scene`)
                The Model portion of the Model-View-Controller paradigm.

            ``gameTimer`` (:class:`PyQt4.QtCore.QTimer`)
                The game timer used to trigger updates to all actors in the scene,
                connected directly to the :func:`model.Scene.advance` method.  Its (and
                therefore the game's) refresh rate is defined by
                :data:`constants.GAME_REFRESH_RATE`.

        **Display Related Variables**
            ``gameStats`` (:class:`view.display.GameStats`)
                The wrapper for the game running checkbox, speed boost progress bar,
                and lives remaining and score lcd scores.

            ``splashImage`` (:class:`PyQt4.QtGui.QPixmap`)
                The pixel map representation of the splash image.

            ``splashBrush`` (:class:`PyQt4.QtGui.QBrush`)
                The brush used to paint when the game is not running, it paints a
                repeated pattern of the ``splashImage``.

            ``viewEffect`` (:class:`PyQt4.QtGui.QGraphicsOpacityEffect`)
                Applied to the splash image to blend it a little with the background
                so it is not so intensely bright orange.

            ``gMessage`` (:class:`PyQt4.QtGui.QGraphicsSimpleTextItem`)
                The game message, displays how many lives are left.

            ``dMessage`` (:class:`PyQt4.QtGui.QGraphicsSimpleTextItem`)
                The directions message, indicating ``Press <space> to Play``, or that
                the game has been won or lost.
    '''
    def __init__(self, app, cpMainWindow):
        ################################################################################
        # Get references to the Qt managed elements, create convenience references to  #
        # the items coming from the generated ui, install the focus filter.            #
        ################################################################################
        self.app          = app
        self.cpMainWindow = cpMainWindow
        self.app.installEventFilter(LostFocusFilter(self, self.cpMainWindow))

        ################################################################################
        # Declare internal state, cannot initialize values for most until later.       #
        ################################################################################
        self.gameRunning  = False
        self.gameFinished = False
        self.livesLeft    = constants.NUM_LIVES
        self.speedIncr    = 0.0

        ################################################################################
        # Configure the View Part 1: setup the game stats bar.                         #
        ################################################################################
        # Warning: if you change the citizen_pac.ui file *and* change the names of these
        # then this will definitely break!
        self.gameStats  = GameStats(cpMainWindow.statsBarCheckBox,
                                    cpMainWindow.statsBarGameSpeedProgress,
                                    cpMainWindow.statsBarLivesValue,
                                    cpMainWindow.statsBarScoreValue)
        self.gameStats.setLives(self.livesLeft)

        ################################################################################
        # Portion 2 of the View: the main drawing window (and scene).                  #
        ################################################################################
        self.view  = self.cpMainWindow.citizenPacGraphicsView
        self.scene = Scene(self, self.view)
        self.cpMainWindow.attachScene(self.scene)
        self.__perform_layout()

        ################################################################################
        # Adaptable render hints, some e.g. scene indexing method.                     #
        ################################################################################
        self.__configure_graphics()

        ################################################################################
        # Game decorations: splash image and instructional text.                       #
        ################################################################################
        self.splashImage      = QtGui.QPixmap(":/view/qt_configs/images/citizen_pac.png")
        self.splashImageBrush = QtGui.QBrush(self.splashImage)
        self.viewEffect       = QtGui.QGraphicsOpacityEffect()
        self.gMessage         = QtGui.QGraphicsSimpleTextItem()
        self.dMessage         = QtGui.QGraphicsSimpleTextItem()
        self.__decorate()

        ################################################################################
        # Last but not least, create the timer and link it to the scene.               #
        ################################################################################
        self.gameTimer = QtCore.QTimer()
        self.gameTimer.timeout.connect(self.scene.advance)
        # Note: the game has not started!  self.gameTimer.start() is performed in the
        # gameRunningSwitched method.
        self.gameTimer.setInterval(constants.GAME_REFRESH_RATE)

    ####################################################################################
    #
    ##
    ### Private interface: methods not to be called by outside classes.
    ##
    #
    ####################################################################################
    def __perform_layout(self):
        '''
        This method is responsible for configuring the window and scene sizes, including
        generating all of the food and setting the correct keyboard focus of the entire
        application.
        '''
        # We need the dimensions of the QGraphicsView item _before_ we can compute the
        # sizes, see http://stackoverflow.com/a/8024124/3814202
        self.cpMainWindow.show()
        self.cpMainWindow.layout().invalidate()
        self.cpMainWindow.hide()

        # Now that the layout manager has been executed, we can query the actual
        # starting width and height of the QGraphicsView instance to intialize the
        # starting locations of all the actors in the scene.
        vRect       = self.view.contentsRect()
        width       = vRect.width()
        height      = vRect.height()
        half_width  = width  * 0.5
        half_height = height * 0.5

        # Set the bounding regions of the scene (this is what defines the coordinate
        # system of the entire game).
        self.scene.setSceneRect(-half_width, -half_height, width, height)

        # Create all the actors and set the speedIncr now that we have the total food
        self.scene.generate(width, height)
        fLen = float(len(self.scene.food))
        if fLen == 0.0:
            self.speedIncr = 0.0
        else:
            self.speedIncr = (constants.MAX_SPEED - constants.GAME_SPEED_START) / fLen

        # Since we want all keyboard input to apply to the scene (e.g. even if the mouse
        # is focused over the scoreboard), now that the context has been initialized we
        # can also direct the QGraphicsView that contains the scene to capture all of
        # the keyboard input.
        self.view.grabKeyboard()

    def __configure_graphics(self):
        '''
        This method configures a couple of Qt specific flags for rendering order and
        scene indexing, as well as connects the view - scene link so that the view can
        perform various back references.  Cannot be done at time of instantiation.
        '''
        self.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        # self.view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        self.view.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

    def __decorate(self):
        '''
        This method creates the effects / text necessary for displaying game controls as
        well as messages related to whether or not the game is finished.
        '''
        # Decoration related fields.  The background image for the pause menu, and the
        # text fields that get shown when the game is paused.
        self.view.setGraphicsEffect(self.viewEffect)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        pen   = QtGui.QPen(QtGui.QColor(255, 255, 255), QtCore.Qt.SolidLine)
        pen.setWidth(2)

        # Game message
        self.gMessage.setBrush(brush)
        self.gMessage.setPen(pen)
        self.gMessage.setFont(QtGui.QFont("mono", 36))

        # Directions message
        self.dMessage.setFont(QtGui.QFont("mono", 36))
        self.dMessage.setText("Press <space> to Play!")
        self.dMessage.setBrush(brush)
        self.dMessage.setPen(pen)

        # Configure the messages width and height, background opacity etc
        self.__paint_messages()
        self.__position_text()

        # Now that their sizes have been computed, add them to the scene.  Technically
        # CitizenPac, the Ghosts, and Food can all "collide" with these, but the Scene
        # method only considers collisions between CitizenPac and Ghosts / Food so it
        # doesn't really matter.
        #
        # What is important is to make sure that these messages get added to the scene
        # *LAST* so that their z-index takes precedence.  AKA they get painted after all
        # of the other actors in the scene, so they show up on top (which is what we
        # want since they are direction messages).
        self.scene.addItem(self.gMessage)
        self.scene.addItem(self.dMessage)

    def __paint_messages(self):
        '''
        Depending on whether or not the game is running, or as been won / lost, display
        a message to show instead of the game.
        '''
        # If the game is resumed / started (the space bar was hit), reset the opacity
        # to be 1 and hide the messages for how to play / number of lives left.
        if self.gameRunning:
            self.view.setBackgroundBrush(QtGui.QBrush())
            self.viewEffect.setOpacity(1.0)
            self.gMessage.hide()
            self.dMessage.hide()
        # Otherwise, the game was just paused either from the space bar, the game was
        # won, or the game was lost
        else:
            # Grammar correctness
            if self.livesLeft == 1.0:
                life = "Life"
            else:
                life = "Lives"
            # Show how many lives are remaining
            msg = "{} {} Remaining...".format(int(self.livesLeft), life)
            self.gMessage.setText(msg)
            self.gMessage.show()
            # Make the background the splash image and slightly darker
            self.viewEffect.setOpacity(0.6)
            self.view.setBackgroundBrush(self.splashImageBrush)
            # If the game is over, indicate this
            if self.livesLeft == 0.0:
                self.dMessage.setText("...game over.")
                self.__position_text()  # make sure to reconfigure the positions
            # If the game is won, indicate this
            elif self.gameFinished:
                self.dMessage.setText("YOU WIN!!!")
                self.__position_text()  # make sure to reconfigure the positions
            # Display the dMessage (will be the original press space to play if the
            # game has just been paused).
            self.dMessage.show()

    def __position_text(self):
        '''
        This method computes the proper location to display the top and bottom messages
        based off of their current bounding rectangles.  When changing the value of the
        text i.e. from __paint_messages, make sure to recompute the text positions.
        '''
        # Location of the lives left message
        gBounds = self.gMessage.boundingRect()
        gWidth  = gBounds.width()
        gHeight = gBounds.height()
        self.gMessage.setPos(-gWidth * 0.5, -gHeight * 0.5)

        # Location of the directions message (press space, game over, game won)
        dBounds = self.dMessage.boundingRect()
        dWidth  = dBounds.width()
        dHeight = dBounds.height()
        self.dMessage.setPos(-dWidth * 0.5, (gHeight + dHeight) * 0.5)

    ####################################################################################
    #
    ##
    ### Public interface: methods called by other components to signal to the controller
    ##                    some form of important action occurred.
    #
    ####################################################################################
    def appLostFocus(self):
        '''
        When the application has lost focus, make sure to force CitizenPac to stop
        moving.  This is called from the :class:`controller.LostFocusFilter` instance
        created in the constructor of this class.  Without this, because of how the
        movement is being represented, CitizenPac would keep moving on their own!  For
        example, if you hold the ``w`` key and then switch to a different application,
        the ``w`` released event was never sent so CitizenPac keeps moving ``North``.
        '''
        if self.scene and self.scene.citizenPac:
            self.scene.citizenPac.setStationary()

    def errorOut(self):
        '''
        Convenience method for students to be able to see slightly more pretty error
        messages.  Since some of the code they are writing happens after the full Qt
        Context is initialized, the error message would keep printing over and over
        in the console.  This method changes the central widget of the ``cpMainWindow``
        to be a "text editor" (read only) that displays the error message.

        .. note::

           Calling this method should only ever be done from **within** an ``except``
           clause.  Example:

           .. code-block:: py

              try:
                  call_some_functions()
              except:
                  self.controller.errorOut()

           This method extracts the traceback on its own.  So if you call it and there
           is no actual traceback, it will be more confusing than helpful.  If anything,
           ``raise`` an exception yourself.
        '''
        self.gameRunning = False
        # You can ignore this code.  It has to be done within the except clause
        # that the exception occurred in.  Just getting more information to
        # display.
        import traceback
        import sys
        if sys.version[0] == "2":
            # Python 2 StringIO
            from cStringIO import StringIO
        else:
            # Python 3 StringIO
            from io import StringIO
        errStream = StringIO()
        traceback.print_exc(file=errStream)
        excDesc = errStream.getvalue()
        errStream.close()

        # THIS CODE IS ADAPTED FROM THE SYNTAXHIGHLIGHTER EXAMPLE AND RETAINS THE SAME
        # LICENSE TERMS.  SEE THE HIGHLIGHTER CLASS BELOW FOR MORE INFORMATION.
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(16)

        editor = QtGui.QTextEdit()
        editor.setFont(font)
        editor.setReadOnly(True)

        highlighter = Highlighter(editor.document())  # noqa F841

        import textwrap
        editor.setPlainText(
            "{}{}".format(
                textwrap.dedent('''
                    There was an error running the code you are developing.  The exception
                    message and traceback were:
                '''),
                excDesc
            )
        )

        self.cpMainWindow.setCentralWidget(editor)
        # END SYNTAXHIGHLIGHTER EXAMPLE CODE

    def foodConsumed(self):
        '''
        This method computes the current score and (if :data:`constants.USE_SPEED_BOOST`
        is set to ``True``) current game speed.  The score and speed are computed using
        the :func:`model.Scene.numFoodEaten` method.  This method is also called by
        :func:`controller.CitizenPac.lostLife` to reset the score and speed boost
        since the food have all been reinitialized.
        '''
        # Calculate and set the current game score
        currScore = self.scene.numFoodEaten() * constants.FOOD_VALUE
        self.gameStats.displayGameScore(currScore)

        # Increase the speed
        if constants.USE_SPEED_BOOST:
            # Calculate and set the current game speed
            speed = constants.GAME_SPEED_START + (self.speedIncr * self.scene.numFoodEaten())
            constants.setGameSpeed(speed)

            # Compute the boost to display
            boost = (constants.gameSpeed - constants.GAME_SPEED_START) / \
                    (constants.MAX_SPEED - constants.GAME_SPEED_START)
            boost = round(boost * 100.0)
            self.gameStats.displayGameSpeed(boost)

    def gameWon(self):
        '''
        When the game is won, this method triggers the game won message to be displayed
        by setting ``self.gameFinished = True`` and calling the
        :func:`controller.CitizenPac.gameRunningSwitched` method.
        '''
        self.gameFinished = True
        self.gameRunningSwitched()

    def gameRunningSwitched(self):
        '''
        The game running state can be switched when one of three events occur:

        1. The user hit the space bar, to pause or resume the game.
        2. A life was lost (:func:`controller.CitizenPac.lostLife`)
        3. The game was won (:func:`controller.CitizenPac.gameWon`)

        The method then propagates to the scene whether or not the game is running,
        starts / stops the game timer, and triggers the pause / game won / game lost
        screen to be displayed if the game is not running.
        '''
        self.gameRunning = not self.gameRunning and self.livesLeft > 0.0 and not self.gameFinished
        self.gameStats.setRunning(self.gameRunning)
        self.scene.setRunning(self.gameRunning)

        if self.gameRunning:
            self.gameTimer.start()
        else:
            self.gameTimer.stop()

        self.__paint_messages()

    def lostLife(self):
        '''
        When CitizenPac collides with a ghost in the :func:`model.Scene.advance` method,
        this method is called to update the scoreboards.  It proceeds by performing

        1. Updating the number of lives left on the scoreboard and switching the game
           running state via :func:`controller.CitizenPac.gameRunningSwitched`.
        2. Resetting the entire scene via :func:`model.Scene.reset`.
        3. Resetting the score and speed boost via :func:`controller.CitizenPac.foodConsumed`.
        '''
        # Decrease the lives and pause or end the game depending on number of lives
        self.livesLeft -= 1
        self.gameStats.setLives(self.livesLeft)
        self.gameRunningSwitched()

        # Reset the scene
        try:
            self.scene.reset()
        except:
            self.errorOut()

        # Reset the score and game speed
        self.foodConsumed()


# The below copyright notice and code comes from the PyQt4 examples, borrowing
# their syntax highlighter to display error messages.
#############################################################################
##
##
##
#############################################################################
class Highlighter(QtGui.QSyntaxHighlighter):
    '''
    This class is part of the PyQt4 example code distributed under the BSD
    license.  It comes from the ``syntaxhighlighter`` example.  The license:

    ..

        Copyright (C) 2010 Riverbank Computing Limited.
        Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
        All rights reserved.

        This file is part of the examples of PyQt.

        ``$QT_BEGIN_LICENSE:BSD$``

        You may use this file under the terms of the BSD license as follows:

        "Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are
        met:

        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in
          the documentation and/or other materials provided with the
          distribution.
        * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
          the names of its contributors may be used to endorse or promote
          products derived from this software without specific prior written
          permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
        "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
        LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
        A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
        OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
        SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
        LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
        DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
        THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."

        ``$QT_END_LICENSE$``
    '''
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QtGui.QTextCharFormat()

        # We have a dark background, use different colors
        # <3 Monokai: http://www.colourlovers.com/palette/1718713/Monokai
        orchid = QtGui.QColor(249, 38, 114)
        bounded_rationality = QtGui.QColor(102, 217, 239)
        night_sand = QtGui.QColor(117, 113, 94)
        yellow = QtGui.QColor(230, 219, 116)
        henn1nk = QtGui.QColor(166, 226, 46)

        # keywordFormat.setForeground(QtCore.Qt.darkBlue)
        keywordFormat.setForeground(orchid)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)

        keywordPatterns = [
            "\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
            "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
            "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
            "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
            "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
            "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
            "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
            "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
            "\\bvolatile\\b"
        ]

        self.highlightingRules = [
            (QtCore.QRegExp(pattern), keywordFormat) for pattern in keywordPatterns
        ]

        classFormat = QtGui.QTextCharFormat()
        classFormat.setFontWeight(QtGui.QFont.Bold)
        classFormat.setForeground(bounded_rationality)
        # classFormat.setForeground(QtCore.Qt.darkMagenta)
        self.highlightingRules.append((QtCore.QRegExp("\\bQ[A-Za-z]+\\b"), classFormat))

        singleLineCommentFormat = QtGui.QTextCharFormat()
        # singleLineCommentFormat.setForeground(QtCore.Qt.red)
        singleLineCommentFormat.setForeground(night_sand)
        self.highlightingRules.append((QtCore.QRegExp("//[^\n]*"), singleLineCommentFormat))

        self.multiLineCommentFormat = QtGui.QTextCharFormat()
        # self.multiLineCommentFormat.setForeground(QtCore.Qt.red)
        self.multiLineCommentFormat.setForeground(night_sand)

        quotationFormat = QtGui.QTextCharFormat()
        # quotationFormat.setForeground(QtCore.Qt.darkGreen)
        quotationFormat.setForeground(yellow)
        self.highlightingRules.append((QtCore.QRegExp("\".*\""), quotationFormat))

        functionFormat = QtGui.QTextCharFormat()
        functionFormat.setFontItalic(True)
        # functionFormat.setForeground(QtCore.Qt.blue)
        functionFormat.setForeground(henn1nk)
        self.highlightingRules.append((QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()"), functionFormat))

        self.commentStartExpression = QtCore.QRegExp("/\\*")
        self.commentEndExpression = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        ''' Highlights the text based off the rules defined in the constructor. '''
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength)
