#Saachi Gopal sg932
'''
The actors.
'''

import json
import random
import textwrap
from PyQt4 import QtCore, QtGui

import constants


class Actor(QtGui.QGraphicsItem):
    '''
    The primary base class for all Actors that are to be added to the scene for game
    play.  If you decide to extend the game and introduce more types of actors, you must
    inherit from this class.

    :Attributes:
        ``scene`` (:class:`model.Scene`)
            The Scene that this actor is bound to.

        ``moveFlags`` (int)
            An integer that embeds the representation of the direction this Actor is
            currently moving in.  This integer is used in conjunction with bitmasking,
            and may only contain the values represented by :data:`constants.STATIONARY`
            ``|`` :data:`constants.MOVE_NORTH` ``|`` :data:`constants.MOVE_SOUTH` ``|``
            :data:`constants.MOVE_EAST` ``|`` :data:`constants.MOVE_WEST`.

        ``cx`` (float)
            The starting location :math:`c_x` of this Actor, saved so that the game can
            be reset.

        ``cy`` (float)
            The starting location :math:`c_y` of this Actor, saved so that the game can
            be reset.

    The coordinate :math:`(c_x, c_y)` represents the **center** of the Actor's starting
    location, and should never change.  To acquire the *current* position of the actor,
    use the ``x()`` and ``y()`` methods respectively, these methods are inherited from
    the :class:`PyQt4.QtGui.QGraphicsItem` class.
    '''
    NORTH = QtCore.QPointF(0.0, -1.0)
    ''' A :class:`PyQt4.QtCore.QPointF` representing the direction ``North``. '''

    SOUTH = QtCore.QPointF(0.0, 1.0)
    ''' A :class:`PyQt4.QtCore.QPointF` representing the direction ``South``. '''

    EAST  = QtCore.QPointF(1.0, 0.0)
    ''' A :class:`PyQt4.QtCore.QPointF` representing the direction ``East``. '''

    WEST  = QtCore.QPointF(-1.0, 0.0)
    ''' A :class:`PyQt4.QtCore.QPointF` representing the direction ``West``. '''

    def __init__(self, scene, cx, cy):
        super(Actor, self).__init__(scene=scene)
        self.cx        = cx
        self.cy        = cy
        self.scene     = scene
        self.moveFlags = constants.STATIONARY

    def boundingRect(self):
        '''
        Returns the bounding rectangle for this Actor.  This is used by the graphics
        backend to determine things such as collisions, whether or not the Actor should
        be drawn (e.g. if it is not visible, don't waste time).

        .. note::

           **All** subclasses must override this method.

        :Return:
            :class:`PyQt4.QtCore.QRectF`
                The bounding rectangle of the actor's current position.
        '''
        return NotImplemented

    def paint(self, painter, option, widget):
        '''
        The method that is responsible for drawing this Actor.

        You need not be concerned with the details of this method.  Refer to the parent
        class :class:`PyQt4.QtGui.QGraphicsItem` documentation on this method for more
        information.

        .. note::

           **All** subclasses must override this method.
        '''
        pass

    def queueMove(self, direction, press):
        '''
        Adds or removes the direction to this Actors' move flags.

        :Parameters:
            ``direction`` (int)
                The direction to add or remove from ``self.moveFlags``.

            ``press`` (bool)
                Whether the key corresponding to this direction is being pressed.
                ``True`` if coming from a key press event, ``False`` if the key is being
                released.

        :Preconditions:
            *Direction Value*
                ``direction`` may only be one of :data:`constants.MOVE_NORTH`,
                :data:`constants.MOVE_SOUTH`, :data:`constants.MOVE_EAST`, or
                :data:`constants.MOVE_WEST`.  Any other values will yield varied and
                unreliable results.
        '''
        if press:
            self.moveFlags |= direction
        else:
            self.moveFlags &= ~direction

    def isStationary(self):
        '''
        Returns whether or not this Actor is currently moving.

        :Return:
            ``bool``
                ``True`` if this Actor is **not** moving, ``False`` otherwise.
        '''
        return self.moveFlags == constants.STATIONARY

    def setStationary(self):
        '''
        Stops the actor from moving by settings its ``moveFlags`` to be
        :data:`constants.STATIONARY`.
        '''
        self.moveFlags = constants.STATIONARY

    def isMoveDirection(self, direction):
        '''
        Returns whether or not this Actor is currently moving in the specified direction.

        :Parameters:
            ``direction`` (int)
                The direction to test whether or not the Actor is currently moving in.

        :Return:
            ``bool``
                ``True`` if the Actor is moving in the specified direction, ``False``
                otherwise.

        :Preconditions:
            *Direction Value*
                ``direction`` may only be one of :data:`constants.MOVE_NORTH`,
                :data:`constants.MOVE_SOUTH`, :data:`constants.MOVE_EAST`, or
                :data:`constants.MOVE_WEST`.  Any other values will yield varied and
                unreliable results.
        '''
        return (self.moveFlags & direction) == direction

    def reset(self):
        '''
        Resets the starting position of this Actor and makes it stationary.  This
        implementation can be overriden, but it is important that this code is actually
        executed.  Refer to the implementation of :func:`view.actors.Food.reset` for
        how to do this.

        The position is reset to ``(self.cx, self.cy)``, and ``self.moveFlags`` is reset
        to be :data:`constants.STATIONARY`.
        '''
        self.setPos(self.cx, self.cy)
        self.setStationary()

    def advance(self, phase):
        '''
        Updates the current position of this Actor depending on the value of its current
        move flags.

        :Parameters:
            ``phase`` (int)
                The update phase.  For this framework, we only need to worry about when
                the second phase occurs, which is when ``phase == 1``.  Refer to the
                ``advance`` documentation for the parent class
                :class:`PyQt4.QtGui.QGraphicsItem`
        '''
        if phase == 1:
            # Short-circuit if we are not supposed to move
            if self.isStationary():
                return

            move = QtCore.QPointF(0.0, 0.0)

            # TODO: update the variable `move` accordingly.
            
            if self.isMoveDirection(constants.MOVE_NORTH) == True:
                move = move + QtCore.QPointF(0.0, -1.0)       
            if self.isMoveDirection(constants.MOVE_SOUTH) == True:
                move = move + QtCore.QPointF(0.0, 1.0)
            if self.isMoveDirection(constants.MOVE_EAST) == True:
                move = move + QtCore.QPointF(1.0, 0.0)
            if self.isMoveDirection(constants.MOVE_WEST) == True:
                move = move + QtCore.QPointF(-1.0, 0.0)
            
            # Using the computed move direction, update the position.
            
            currPos = QtCore.QPointF(self.x(), self.y())
            self.setPos(currPos + constants.gameSpeed * move)
            self.update()


class Food(Actor):
    '''
    Animated food.
    '''
    def __init__(self, scene, cx, cy, color, radius):
        super(Food, self).__init__(scene, cx, cy)

        self.outerRadius = radius
        self.innerRadius = 0.5 * self.outerRadius

        self.outerColor = color
        red   = 255 - color.red()
        green = 255 - color.green()
        blue  = 255 - color.blue()
        self.innerColor = QtGui.QColor(red, green, blue)

        self.outerSweep = 360.0
        self.innerSweep = 0.0
        self.decreasing = True

        self.innerBoundingRect = self.computeBoundingRect(self.innerRadius)
        self.outerBoundingRect = self.computeBoundingRect(self.outerRadius)

        self.startAngle = random.random() * 360.0

    def computeBoundingRect(self, radius):
        # Find the top left corner
        left        = self.x() - radius
        top         = self.y() - radius
        topLeft     = QtCore.QPointF(left, top)
        # Find the bottom right corner
        right       = self.x() + radius
        bottom      = self.y() + radius
        bottomRight = QtCore.QPointF(right, bottom)
        # Return the bounding rectangle
        return QtCore.QRectF(topLeft, bottomRight)

    def boundingRect(self):
        return self.outerBoundingRect

    def paint(self, painter, option, widget):
        # Paint the outer path first
        outerPath = QtGui.QPainterPath()
        outerPath.arcTo(self.outerBoundingRect, self.startAngle, self.outerSweep)
        # outerPath.addEllipse(self.outerBoundingRect)
        outerPath.closeSubpath()
        painter.setBrush(self.outerColor)
        painter.drawPath(outerPath)

        # Paint the inner path second
        innerPath = QtGui.QPainterPath()
        innerPath.arcTo(self.innerBoundingRect, self.startAngle, self.innerSweep)
        # innerPath.addEllipse(self.innerBoundingRect)
        innerPath.closeSubpath()
        painter.setBrush(self.innerColor)
        painter.drawPath(innerPath)

    def advance(self, phase):
        if phase == 1:
            # If decreasing, reduce outer radius and increase inner radius
            if self.decreasing:
                self.outerSweep -= 1.0
                self.innerSweep += 1.0
                if self.outerSweep == 0.0:
                    self.decreasing = False
            # Otherwise, reverse: increase outer radius and decrease inner radius
            else:
                self.outerSweep += 1.0
                self.innerSweep -= 1.0
                if self.outerSweep == 360.0:
                    self.decreasing = True

            self.update()

    def reset(self):
        '''
        This method resets the ``self.innerRadius`` and ``self.outerRadius`` to the
        initial starting positions, and sets ``self.decreasing`` to ``False``, thus
        "restarting" the animation of the Food.

        After, it calls the ``super`` class ``reset`` method
        (:func:`view.actors.Actor.reset`) so that the position will be reset as well.
        This is necessary, for example, if you wanted to incorporate moving Food into
        the game as well.
        '''
        self.outerRadius = 360.0
        self.innerRadius = 0.0
        self.decreasing  = False
        super(Food, self).reset()


class SplineDrawer(Actor):
    '''
    Do not edit this class.
    '''
    def __init__(self, scene, cx, cy, dataResource, sx, sy):
        super(SplineDrawer, self).__init__(scene, cx, cy)

        # Since we went through the effort of reading in a spline, enable reuse of
        # this directly if desired.  The main game board will not use these because
        # the resolution at which they are drawn makes replacing them with polygons
        # just as good, and takes a fraction of the time to render.
        #
        # Splines are cubic polynomials...
        self.path     = SplineDrawer.parseResourceJson(dataResource, sx, sy)
        self.pathRect = self.path.boundingRect()  # Only compute this once.

        # Extract a usable polygon from the parsed spline drawing path
        sub_poly  = self.path.toSubpathPolygons()
        self.poly = QtGui.QPolygonF()
        for sub in sub_poly:
            for point in sub:
                self.poly.append(point)
        self.polyRect = self.poly.boundingRect()

        self.color = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,
                                  QtCore.qrand() % 256)

    @classmethod
    def parseResourceJson(cls, dataResource, sx, sy):
        # NOTE: yes, this is longer than 40 lines.  Particularly when dealing with
        # IO code (input / output), it tends to get verbose.
        #
        # Use the Qt Resource system to get a file handle on the input json data
        # Throughout this method we rely on "duck-typing", an interesting feature of
        # Python.  For example, note that the `data` variable is only declared when
        # the `if` statement below is True.  The significance is that, if you decide to
        # write code like this, you better be sure that you either (1) error out or
        # (2) define `data` in the else statement.  It depends on the scenario.
        stream = QtCore.QFile(dataResource)
        if stream.open(QtCore.QFile.ReadOnly):
            data = str(stream.readAll())
            stream.close()
        else:
            # Qt style files are more like C/C++, always make sure you close() them.
            # The Python `with` statement does this for you automatically.
            stream.close()
            raise RuntimeError("Unable to read [{}]: {}".format(dataResource,
                                                                stream.errorString()))
        # Parse the json file as a dictionary and obtain the keys we need to construct
        # the spline (every key except for the `closed` key).
        #
        # We use `key=int` to implicitly cast each string key into an integer so that
        # we can sort based off numeric value rather than the ascii value.
        try:
            all_points = json.loads(data)
            all_keys   = sorted(set(all_points.keys()) - set([u"closed"]), key=int)
            num_keys   = len(all_keys)
            closed     = bool(all_points[u"closed"])
        except Exception as e:
            raise RuntimeError(
                "Unable to extract all relevant keys from the json:\n{}".format(e)
            )

        # Declare the necessary bookeeping variables for the loop, and the painter path
        # that we will eventually be returning at the end of the method.
        #
        # The index variable `idx` helps us keep track of when we are at an edge case,
        # refer the the class documentation.  Technically `prev_hL` and `first_hR` do
        # not need to be saved, but if this ever needs to be updated better to have them
        # all available.
        idx = 0
        prev_co = prev_hL = prev_hR = None
        first_co = first_hL = first_hR = None
        painterPath = QtGui.QPainterPath()
        for key in all_keys:
            # Read in the current control point data
            control = all_points[key]
            try:
                # They are stored as lists of strings, convert to float now. Scale by
                # sx and sy come from differing coordinate systems.  We assume the z
                # value is 0.0 (2D game), so we just need to adjust x and y.
                co     = [float(pt) for pt in control[u"co"]]
                co[0] *= sx
                co[1] *= sy

                hL     = [float(pt) for pt in control[u"handle_left"]]
                hL[0] *= sx
                hL[1] *= sy

                hR     = [float(pt) for pt in control[u"handle_right"]]
                hR[0] *= sx
                hR[1] *= sy
            except Exception as e:
                raise RuntimeError(
                    "Could not parse all floats for key [{}]: {}".format(key, e)
                )
            # With how blender stores things, we cannot start making any of the path
            # until we have seen at least two control points.  Save first and move on.
            if idx == 0:
                first_co, first_hL, first_hR = co, hL, hR  # noqa F841
            # For all remaining keys, use previous control point (prev_co) and previous
            # handle_right in conjunction with current handle_left and current control
            # point to draw using Qt's framework.
            elif idx < num_keys:
                painterPath.moveTo(prev_co[0], prev_co[1])
                painterPath.cubicTo(
                    prev_hR[0], prev_hR[1],
                    hL[0], hL[1],
                    co[0], co[1]
                )

            # Update for next loop
            prev_co, prev_hL, prev_hR = co, hL, hR  # noqa F841
            idx += 1

        # If the spline was closed (which we need it to be), then link up the last
        # control point with the first.
        if closed:
            painterPath.moveTo(prev_co[0], prev_co[1])
            painterPath.cubicTo(
                prev_hR[0], prev_hR[1],
                first_hL[0], first_hL[1],
                first_co[0], first_co[1]
            )
        else:
            # Being strict, because we are converting to *closed* polygons
            raise RuntimeError("Only closed Bezier Paths from Blender are supported.")

        return painterPath

    def paint(self, painter, option, widget):
        painter.setBrush(self.color)
        # If you wanted to draw a higher resolution spline, you should uncomment this
        # and comment out the drawPolygon call.  For the size that the SplineActor
        # instances in the framework are drawn, there is no benefit.  But for a larger
        # image you will definitely notice the difference!
        # painter.drawPath(self.path)
        painter.drawPolygon(self.poly)

    def boundingRect(self):
        return self.polyRect


class GhostActor(SplineDrawer):
    '''
    The ghosts.
    '''
    DATA_FILE = ":/view/qt_configs/data/ghost_body.json"
    ''' The data file needed to instantiate a Ghost. '''

    GHOST_MOVE_TIME = 1000
    '''
    How frequently a GhostActor should randomly change its direction.  This time is
    specified in milliseconds, i.e. ``1000`` means **1 second**.
    '''

    def __init__(self, scene, cx, cy, sx, sy):
        super(GhostActor, self).__init__(scene, cx, cy, GhostActor.DATA_FILE, sx, sy)
        self.moveFlags = constants.STATIONARY
        self.moveTimer = QtCore.QTimer()
        self.moveTimer.timeout.connect(self.timerEvent)
        self.moveTimer.start(GhostActor.GHOST_MOVE_TIME)

    def timerEvent(self):
        # shuffle so there is no direction bias
        dirs = [constants.MOVE_NORTH, constants.MOVE_SOUTH,
                constants.MOVE_EAST,  constants.MOVE_WEST]
        random.shuffle(dirs)

        # Either try and remove a direction or add one
        r1 = random.random()
        if r1 < 0.5:
            removed = False
            for d in dirs:
                if (self.moveFlags & d) == d:
                    self.moveFlags &= ~d
                    removed = True
                    break

            # If no directions could be removed, make sure that the moveFlags attribute
            # is set to constants.STATIONARY for consistency
            if not removed:
                self.moveFlags = constants.STATIONARY
        else:
            for d in dirs:
                if not (self.moveFlags & d) == d:
                    self.moveFlags |= d
                    break


class CitizenPacActor(SplineDrawer):
    '''
    Citizen Pac.
    '''
    DATA_FILE = ":/view/qt_configs/data/bat_points.json"
    ''' The data file needed to instantiate a CitizenPac. '''

    def __init__(self, scene, cx, cy, sx, sy):
        super(CitizenPacActor, self).__init__(scene, cx, cy, CitizenPacActor.DATA_FILE, sx, sy)

        self.mx = 0.0
        self.my = 0.0

    def advance(self, phase):
        '''
        See parent class documentation in :func:`view.actors.Actor.advance`.
        '''
        # Grab the current coordinates, call the student move code, then
        # calculate what their move direction was
        if phase == 1 and not constants.FULL_GAME_MODE:
            if phase == 1:
                sx = self.x()
                sy = self.y()
            super(CitizenPacActor, self).advance(phase)
            if phase == 1:
                ex = self.x()
                ey = self.y()
                self.mx = ex - sx
                self.my = ey - sy
                self.printMoveFlags()
        else:
            # If not the right phase or not debug mode, just call super class
            super(CitizenPacActor, self).advance(phase)

    def printMoveFlags(self):
        '''
        Prints the current move direction, and what the previously computed move
        direction was.  Only intended to be called after
        :func:`view.actors.CitizenPacActor.advance`.
        '''
        # Current move flags
        stationary = self.isStationary()
        north = self.isMoveDirection(constants.MOVE_NORTH)
        south = self.isMoveDirection(constants.MOVE_SOUTH)
        east  = self.isMoveDirection(constants.MOVE_EAST)
        west  = self.isMoveDirection(constants.MOVE_WEST)

        # Print out what the actual directions should be
        nx, ny = Actor.NORTH.x(), Actor.NORTH.y()
        sx, sy = Actor.SOUTH.x(), Actor.SOUTH.y()
        ex, ey = Actor.EAST.x(),  Actor.EAST.y()
        wx, wy = Actor.WEST.x(),  Actor.WEST.y()

        print(textwrap.dedent('''
            Move Flags for CitizenPac:

                - Stationary:            {}
                - North -- ({:4.1f}, {:4.1f}): {}
                - South -- ({:4.1f}, {:4.1f}): {}
                - East  -- ({:4.1f}, {:4.1f}): {}
                - West  -- ({:4.1f}, {:4.1f}): {}

            The move direction you just computed was:

                (x = {:4.1f}, y = {:4.1f})

            Recall that the game speed affects this directly!  The current gameSpeed
            from constants.py is:

                {:4.4f}
            {}
        '''.format(stationary, nx, ny, north, sx, sy, south,
                   ex, ey, east, wx, wy, west,
                   self.mx, self.my, constants.gameSpeed, "*" * 44)))
