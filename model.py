#Saachi Gopal sg932
import math
from PyQt4 import QtCore, QtGui

import constants
from view.actors import Actor, CitizenPacActor, GhostActor, Food
from view.display import randomColor

'''
This is the model
'''


def generateFoodGrid(width, height):
    '''
    This method returns a ``list`` of tuples containing all of the coordinates and
    colors for the :class:`view.actors.Food` actors in the scene, given the specified
    ``width`` and ``height`` of the game board in conjunction with some of the constants
    defined in :mod:`constants`.  **No** ``Food`` **objects are to be instantiated directly
    in this method**.  Rather, this method is queried from elsewhere in the framework
    when it is the "appropriate" time to instantiate the ``Food`` objects.  That is,
    given the ``width`` and ``height`` of the game board, this method computes

    1. The total number of ``Food`` objects that can fit in both the horizontal and
       vertical directions.

       - This is done using ``width``, ``height``, and the constants
         :data:`constants.FOOD_RADIUS` and :data:`constants.FOOD_SPARSITY`
       - You are advised to **change** the values of these constants to test your code,
         the default values do not accommodate for all corner cases.  For example, what
         should your code do when you set :data:`constants.FOOD_SPARSITY` to ``1.0``?
         If you set it to ``2.0``?  What if you set :data:`constants.FOOD_RADIUS` to
         be ``23.32``?
       - The total number of ``Food`` items that can fit in the :math:`x` and :math:`y`
         directions are ``nx`` and ``ny``, respectively.  That is, as a sanity check,
         the total length of the list you ``return`` at the end of the method should
         be exactly ``nx * ny``, representing :math:`N = n_x \cdot n_y` total ``Food``
         objects based on the constraints of the problem.

    2. Computes the offset variables for the starting locations of each ``Food`` object,
       taking into account when :data:`constants.FOOD_RADIUS` does not evenly divide
       ``width`` or ``height`` respectively.

       - The variables ``dx`` and ``dy`` in the code correspond to the change in
         position :math:`\Delta x` and :math:`\Delta y`, respectively.
       - The variables ``tx`` and ``ty`` in the code correspond to the global
         translation :math:`t_x` and :math:`t_y`, respectively.

    .. todo::

       3. Using the variables from (1) and (2), compute all ``Food`` coordinate *centers*,
          and create a random color using :func:`view.display.randomColor`.  At the stage
          that this method is called in the framework, this is all that can be computed.

          - **Make sure you set** :data:`constants.FULL_GAME_MODE` **to** ``True`` **,
            otherwise your hard work will never even be called by the framework!!!**

       .. warning::

          As a reminder, you should **not** create *any* ``Food`` objects in this method!

    :Parameters:
        ``width`` (float)
            The total width of the game board at the start of the game (before any
            resizing by the user.)

        ``height`` (float)
            The total height of the game board at the start of the game (before any
            resizing by the user.)

    :Preconditions:
        *Size Constraints*
            ``width`` and ``height`` are both positive, and are both (individually)
            strictly greater than ``2.0 * constants.FOOD_RADIUS *
            constants.FOOD_SPARSITY``.

    :Return:
        ``list``
            A length :math:`N = n_x \cdot n_y` list of **tuples** representing each
            ``Food`` object.  Ensure that the order is exactly correct.  Each element of
            the list should be a ``tuple`` of length ``3``, where the following is true:

            +-------+------------------------------+---------------------------------------------+
            | Index | Type                         | Value                                       |
            +=======+==============================+=============================================+
            | ``0`` | ``float``                    | The center :math:`x` coordinate :math:`c_x`.|
            +-------+------------------------------+---------------------------------------------+
            | ``1`` | ``float``                    | The center :math:`y` coordinate :math:`c_y`.|
            +-------+------------------------------+---------------------------------------------+
            | ``2`` | :class:`PyQt4.QtGui.QColor`  | A random  color. You don't need to construct|
            |       |                              | one on your own, simply call the function   |
            |       |                              | :func:`view.display.randomColor` *already*  |
            |       |                              | imported for you at the top of the file.    |
            +-------+------------------------------+---------------------------------------------+

            .. warning::

               The method calling this function (:func:`model.Scene.generate`) is going
               to loop through what you return similar to

               .. code-block:: py

                  lst = model.generateFoodGrid(w, h)
                  for cx, cy, color in lst:
                      # ... create the actual Food object ...

               So if the code crashes on a line similar to that one, you should inspect
               what you ``append`` to the list ``all_food`` and make sure it adheres to
               the above specification.
    '''
    # Initial setup
    all_food    = []
    half_width  = width * 0.5
    half_height = height * 0.5
    diam        = 2.0 * constants.FOOD_RADIUS
    food_fill   = diam * constants.FOOD_SPARSITY
    half_fill   = food_fill * 0.5

    # 1. Compute the x and y scaling factors
    nx = float(int(width)  / int(food_fill))
    ny = float(int(height) / int(food_fill))
    # constraints: at least 4 food always
    nx = max(nx, 2.0)  # Must be >= 2 since we need to divide by
    ny = max(ny, 2.0)  # nx - 1.0 in the next step!

    # 2. Compute the change in position for x / y directions, and coordinate transforms
    dx = (width  - food_fill) / (nx - 1.0)
    dy = (height - food_fill) / (ny - 1.0)
    # coordinate transformation
    tx = -half_width  + half_fill
    ty = -half_height + half_fill

    # 3. TODO: write step 3!
    # - You *MUST* use *TWO* while loops, one nested inside the other.
    # - You *MUST* use dx, tx, dy, and ty in your computation
    
    i = tx
    j = ty 
    #Inv: rows from tx..i-1 have been processed 
    while i <= -tx:
        xcenter = i
        #Inv: columns from ty..j-1 have been processed
        while j <= -ty:
            ycenter = j
            color = randomColor()
            add = (xcenter, ycenter, color)
            all_food.append(add)
            j = j + dy   
        i = i + dx
        j = ty
    
    return all_food


class Scene(QtGui.QGraphicsScene):
    '''
    The main model of the game, responsible for creating and maintaining the state of
    the actors in the game.   By inheriting from :class:`PyQt4.QtGui.QGraphicsScene`,
    an instance of this class will be receiving the update notifications coming from the
    View *indirectly*.  That is, though this class maintains the locations of the
    different Actors, because it is part of the ``PyQt4`` View framework, it receives
    communication directly from the View in certain portions.

    For example, the :class:`controller.CitizenPac` class maintains a ``gameTimer`` that
    indirectly controls all of the Actors in the scene.  At the end of the constructor
    for that class, the timer is ``connect`` ed to the :func:`model.Scene.advance` method
    in this class.  In essence, this is an indirect "loop", but since the timer is
    officially managed by the View, the impact is that the View technically communicates
    directly with the Model (this class).  This relationship is instigated and
    controlled by the Controller, but we wanted to clarify by example that the
    relationships between the Model, View, and Controller in this framework have blurred
    boundary lines.  If you decide to make your own Model-View-Controller one day, you
    may find yourself in a similar scenario -- the limitations of the ``PyQt4``
    framework in the sense that technically the Model is "directly managed by the View,
    which is indirectly managed by the Controller" are confusing.  However, though the
    relationships between these items become less translucent, its benefits (for
    technical reasons not explained here) are worthy.  The short version: ``PyQt4``
    has a sophisticated backend framework developed over decades by one of the industry
    leaders.  The framework excels at maintaining consistent internal state, and so we
    lean on these features at the expense of "blurred Model-View-Controller"
    relationships.

    :Attributes:
        ``controller`` (:class:`controller.CitizenPac`)
            A reference to the Controller to be able to propagate events received from
            ``PyQt4`` such as collisions back to the Controller so it can decide what
            action to perform.

        ``view`` (:class:`PyQt4.QtGui.QGraphicsView`)
            A pointer to the ``QGraphicsView`` instance that this Scene is bound to.
            This reference is also accessible via the parent class's ``parent`` member,
            stored as ``view`` for convenience.  Every
            :class:`PyQt4.QtGui.QGraphicsScene` instance must be bound to a
            :class:`PyQt4.QtGui.QGraphicsView` instance --- this is how the scene is
            actually displayed.

        ``citizenPac`` (:class:`view.actors.CitizenPacActor`)
            The representation of CitizenPac.

        ``ghosts`` (list)
            A list of :class:`view.actors.GhostActor` instances, representing all of the
            Ghosts in the scene.

        ``food`` (list)
            A list of :class:`view.actors.Food` instances, representing where all of the
            Food in the scene is.

        ``gameRunning`` (bool)
            A boolean representing whether or not the game is currently running.  In
            particular, collision events, moving actors, etc, should not continue
            if the game is not running.  See the :func:`model.Scene.advance` method for
            how it is used.

        ``foodEaten`` (int)
            An integer representing how many Food collisions have been detected.  When
            ``foodEaten == len(self.food)``, the ``controller`` is notified that the
            Game has completed.
    '''
    def __init__(self, controller, view):
        super(Scene, self).__init__(view)
        # Parent references
        self.controller  = controller
        self.view        = view
        # Actor references
        self.citizenPac  = None
        self.ghosts      = []
        self.food        = []
        # Game state convenience members
        self.gameRunning = False
        self.foodEaten   = 0

    def generate(self, width, height):
        '''
        Responsible for creating the initial conditions of the game, including where
        CitizenPac and the Ghosts start, and the location of all the Food.  This method
        calls the :func:`model.generateFoodGrid` method using the width and height of
        the :class:`PyQt4.QtGui.QGraphicsView` instance that this (``self``) instance
        is bound to.

        All instances created are registered using the :func:`model.Scene.registerActor`
        method, which is in turn responsible for storing the the generated actors in the
        related attributes of this instance (i.e. ``self.citizenPac`` or ``self.food``).

        If you want to extend the game to add more types of actors, this is where you
        should create them.

        :Parameters:
            ``width`` (float)
                The starting width of the window we will be drawing to.

            ``height`` (float)
                The starting height of the window we will be drawing to.

        .. warning::

           Do **not** call this method from the constructor.  The
           :class:`controller.CitizenPac` class is responsible for calling this method.
           Because of the "blurred Model-View-Controller" relationships, the ``Scene``
           must be instantiated before the View has completed initialization.  In order
           to use the *correct* ``width`` and ``height``, initialization of the actors
           in the scene must be deferred until **after** the View's Layout has been
           performed (this is controlled by ``PyQt4``).
        '''
        # Generate the CitizenPac and Ghost actors.  By default, they are dispersed in
        # a circular pattern.  There can only be one CitizenPac
        nActors = float(constants.NUM_GHOSTS + 1)  # All ghosts plus CitizenPac
        two_pi  = 2.0 * math.pi
        for i in range(int(nActors)):
            # Create the new x and y coordinates on the circle
            t  = (i * two_pi) / nActors
            cx = math.sin(t) * constants.DISPERSION_RADIUS
            cy = math.cos(t) * constants.DISPERSION_RADIUS

            # The constructor arguments are the same for both, but the class is
            # different.  We negative scaling for the y coordinate because the
            # the Qt coordinate system is positive y down.
            args = [self, cx, cy, constants.SPLINE_COORD_SCALE, -constants.SPLINE_COORD_SCALE]

            # If it is the first iteration, create CitizenPac (always at the bottom)
            actor = CitizenPacActor(*args) if i == 0 else GhostActor(*args)

            # Make sure to register the actor!
            self.registerActor(actor, cx, cy)

        # Generate all of the Food
        if constants.FULL_GAME_MODE:
            try:
                food_coords = generateFoodGrid(width, height)
                for cx, cy, color in food_coords:
                    food = Food(self, cx, cy, color, constants.FOOD_RADIUS)
                    self.registerActor(food, cx, cy)
            except:
                self.controller.errorOut()

    def registerActor(self, actor, cx, cy):
        '''
        Registers an :class:`view.actors.Actor` with this Scene.  This method **must**
        be called for the game mechanics (e.g. collisions) to be detected.  It is
        assumed that the actor being registered has already been added to the
        ``PyQt4`` side of the scene by construction.  That is, the
        :func:`model.Scene.generate` function will instantiate an actor passing ``self``
        as the first parameter.  Since each actor extends the
        :class:`PyQt4.QtGui.QGraphicsItem` class, the item is automatically added to the
        Scene.  Alternatively, you can call the ``addItem`` method (inherited from the
        :class:`PyQt4.QtGui.QGraphicsScene` class) to associated the item with the
        graphics backend.

        After construction, the `PyQt4.QGraphicsItem` class has not had its position
        set.  The ``setPos`` function is called at the end of this method, assuming it
        was an instance of a class we are currently tracking.

        :Parameters:
            ``actor`` (:class:`view.display.Actor`)
                An :class:`view.display.Actor` instance.  Currently the only classes
                that are registered are

                1. :class:`view.display.CitizenPacActor` (stored in ``self.citizenPac``).
                2. :class:`view.display.GhostActor` (appended to ``self.ghosts``).
                3. :class:`view.display.Food` (appended to ``self.food``).

                If you want to extend the game to allow more actors, declare the
                appropriate variables in the constructor of this class to maintain their
                state, and register them here.

            ``cx`` (float)
                The :math:`x` coordinate of the actor.

            ``cy`` (float)
                The :math:`y` coordinate of the actor.

        :Preconditions:
            *Size Constraints*
                The parameters ``cx`` and ``cy`` are assumed to be valid coordinates
                for this scene.  If they are not, the actor will simply be "displayed"
                off-screen.
        '''
        if not actor:
            raise RuntimeError("Actor was None, and therefore cannot be registered.")

        # Associate the actor with the related member field.  Extending the game?  Add
        # more member variables in the constructor to maintain tracking them, and check
        # the type here.
        #
        # You will also need to update the `advance` method of this class to check for
        # collisions with these new types of actors.
        if type(actor) is CitizenPacActor:
            if self.citizenPac:
                raise RuntimeError("There can only be one CitizenPac per game!")
            self.citizenPac = actor
        elif type(actor) is Food:
            self.food.append(actor)
        elif type(actor) is GhostActor:
            self.ghosts.append(actor)
        else:
            raise RuntimeError(
                "Unknown actor of type [{}] cannot be registered.".format(type(actor))
            )

        # If we get to this point, then we know that the actor provided inherits from
        # the view.actors.Actor class, and therefore will have the setPos function.
        actor.setPos(cx, cy)

    def numFoodEaten(self):
        return self.foodEaten

    def setRunning(self, running):
        self.gameRunning = running

    def reset(self):
        '''
        This method resets the game state for the actors *that change locations*.  It
        should not modify any instances directly, rather, call the
        :func:`view.actors.Actor.reset` for the appropriate entities of this instance.
        '''
        # TODO: implement the reset
        for ghost in self.ghosts:
            ghost.reset()
        
        self.citizenPac.reset() 
        self.foodEaten = 0
        
        for food in self.food:
            food.reset()
            food.show()
        

    def wrapActor(self, actor, width, height):
        '''
        This method is responsible for adjusting the position of an Actor so that it
        remains within the confines of the game grid.

        .. tip::

            Refer to the :ref:`coordinates` section of the writeup

        :Parameters:
            ``actor`` (:class:`view.actors.Actor`)
                The actor to modify the position of, based off ``width`` and ``height``.

            ``width`` (float)
                The width of the bounding rectangle that defines the coordinate system
                for this scene.

            ``height`` (float)
                The height of the bounding rectangle that defines the coordinate system
                for this scene.

        :Preconditions:
            **Size Constraints**
                The ``width`` and ``height`` must be greater than or equal to ``1.0``.
        '''
        # Failsafe: make sure it is not None
        if not actor:
            return

        # Failsafe: make sure it is an actor we can work with.
        # Exercise: why can't we use `type(actor) is not Actor`?
        if not isinstance(actor, Actor):
            return

        # TODO:
        # Recall that to get the current position of the actor, you can call the
        
        xpos = actor.x()
        ypos = actor.y()
        
        if actor.x() < -.5*width:
            xpos += width
        if actor.x() > .5*width:
            xpos -= width
        if actor.y() < -.5*height:
            ypos += height
        if actor.y() > .5*height:
            ypos -= height
        
        return actor.setPos(xpos, ypos)
        
        ################################################################################
        # DO NOT MODIFY !!!                                                            #
        # After you call ``actor.setPos(computed_x, computed_y)``, the ``update()``    #
        # method signals to the drawing framework that it needs to repaint this actor. #
        actor.update()                                                                 #
        ################################################################################

    def wrapRelevantActors(self):
        # Acquire the width and height of the current bounding rectangle
        bounds = self.sceneRect()
        width = bounds.width()
        height = bounds.height()

        # Wrap the actors that can move in the game
        self.wrapActor(self.citizenPac, width, height)
        for ghost in self.ghosts:
            self.wrapActor(ghost, width, height)

    def advance(self):
        '''
        Process collisions.
        '''
        if self.gameRunning and constants.FULL_GAME_MODE:
            for ghost in self.ghosts:
                if self.citizenPac.collidesWithItem(ghost):
                    self.controller.lostLife()
                    return

            for food in self.food:
                if food.isVisible() and self.citizenPac.collidesWithItem(food):
                    food.hide()
                    self.foodEaten += 1
                    self.controller.foodConsumed()

            if self.foodEaten == len(self.food):
                self.controller.gameWon()

        self.wrapRelevantActors()
        super(Scene, self).advance()

    def keyPressEvent(self, e):
        key = e.key()

        if key == QtCore.Qt.Key_W:
            self.citizenPac.queueMove(constants.MOVE_NORTH, True)
        elif key == QtCore.Qt.Key_S:
            self.citizenPac.queueMove(constants.MOVE_SOUTH, True)
        elif key == QtCore.Qt.Key_D:
            self.citizenPac.queueMove(constants.MOVE_EAST, True)
        elif key == QtCore.Qt.Key_A:
            self.citizenPac.queueMove(constants.MOVE_WEST, True)
        else:
            super(Scene, self).keyPressEvent(e)

    def keyReleaseEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key_W:
            self.citizenPac.queueMove(constants.MOVE_NORTH, False)
        elif key == QtCore.Qt.Key_S:
            self.citizenPac.queueMove(constants.MOVE_SOUTH, False)
        elif key == QtCore.Qt.Key_D:
            self.citizenPac.queueMove(constants.MOVE_EAST, False)
        elif key == QtCore.Qt.Key_A:
            self.citizenPac.queueMove(constants.MOVE_WEST, False)
        elif key == QtCore.Qt.Key_Space:
            self.controller.gameRunningSwitched()
        else:
            super(Scene, self).keyPressEvent(e)
