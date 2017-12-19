'''
The ``constants`` module defines different variables that are to be used consistently
throughout the rest of the framework.  When developing the assignment you are more than
allowed to change **some** of the values in this file.  For example, you could change
the :data:`constants.FOOD_RADIUS` and/or :data:`constants.FOOD_SPARSITY` constants to
help test whether or not you are placing the food in the correct location or not.

.. danger::

   Under **no** circumstances should you change any of :data:`constants.STATIONARY`,
   :data:`constants.MOVE_NORTH`, :data:`constants.MOVE_SOUTH`,
   :data:`constants.MOVE_EAST`, or :data:`constants.MOVE_WEST`.

   These constants are being used as a "bit-masking enum" to control the movement of
   the :class:`view.actors.Actor` instances (CitizenPac and the Ghosts).  It is very
   important that you do not change these values, else the game mechanics will produce
   undefined behavior.
'''

__all__ = [
    "STATIONARY", "MOVE_NORTH", "MOVE_SOUTH", "MOVE_EAST", "MOVE_WEST",
    "GAME_SPEED_START", "gameSpeed", "setGameSpeed", "MAX_SPEED", "USE_SPEED_BOOST",
    "FOOD_RADIUS", "FOOD_SPARSITY", "SPLINE_COORD_SCALE",
    "FOOD_VALUE", "FULL_GAME_MODE", "NUM_LIVES", "NUM_GHOSTS", "DISPERSION_RADIUS"
]

########################################################################################
# Actor movement related constants.                                                    #
########################################################################################

STATIONARY = (1 << 0)
''' Represents the stationary state of :class:`view.actors.Actor`. '''

MOVE_NORTH = (1 << 1)
''' Represents when :class:`view.actors.Actor` should move ``North``. '''

MOVE_SOUTH = (1 << 2)
''' Represents when :class:`view.actors.Actor` should move ``South``. '''

MOVE_EAST  = (1 << 3)
''' Represents when :class:`view.actors.Actor` should move ``East``. '''

MOVE_WEST  = (1 << 4)
''' Represents when :class:`view.actors.Actor` should move ``West``. '''

########################################################################################
# Game Speed related constants / function.                                             #
########################################################################################

GAME_SPEED_START = 2.0
''' The starting speed of the game.  Must always be strictly positive (:math:`> 0`).'''

gameSpeed        = GAME_SPEED_START
'''
The current speed of the game, initialized as :data:`constants.GAME_SPEED_START`.  To
update the value of the game speed, call :func:`constants.setGameSpeed`.
'''

MAX_SPEED        = 10.0
'''
The maximum game speed.  Feel free to play with this variable, the larger you increase
its value, the more "overdraw" will occur and the harder it will be to actually
complete the game.  Must be strictly greater than :data:`constants.GAME_SPEED_START`.
'''

USE_SPEED_BOOST = True
'''
When set to ``False`` the speed of all the actors will remain the same throughout the
duration of the game.  If you set this to ``True``, an entertaining (but much more
difficult to win) variant of the game is used where the more food CitizenPac eats, the
faster all of the actors move.  The game speed will start at
:data:`constants.GAME_SPEED_START`, and increase to :data:`constants.MAX_SPEED`.
'''


def setGameSpeed(val):
    '''
    Wrapper method to allow updating the global variable :data:`constants.gameSpeed` in
    this module from another module, without necessitating ``from Constants import *``.

    This sets the value of :data:`constants.gameSpeed` to ``val``.

    :Parameters:
        ``val`` (float)
            The value to set :data:`constants.gameSpeed` to.
    '''
    global gameSpeed
    gameSpeed = val


########################################################################################
# Actor sizing related constants.                                                      #
########################################################################################
FOOD_RADIUS        = 10.0
''' The radius for the :class:`view.actors.Food` class. '''

FOOD_SPARSITY      = 5.0
'''
The *sparsity* factor for dispersing the :class:`view.actors.Food` grid, used in the
:func:`model.generateFoodGrid` function.
'''

SPLINE_COORD_SCALE = 4.0
'''
The software that the :class:`view.actors.CitizenPacActor` and
:class:`view.actors.GhostActor` classes were designed in (Blender) were modeled at a
different scale, you can use this to control how big or small the CitizenPac and Ghosts
are.  This constant must be positive and non-zero.
'''

########################################################################################
# Game Mechanics related constants.                                                    #
########################################################################################
FOOD_VALUE         = 111.0
''' The value each :class:`view.actors.Food` consumed is worth in points. '''

FULL_GAME_MODE     = True
'''
Before you begin working on the function :func:`model.generateFoodGrid`, you will want
to keep this as ``False`` so that the game will still run and you can test whether or
not the code you have written to move the CitizenPac and Ghosts is working correctly.

This constant has three important consequences:

1. If set to ``False``, no collisions are processed for **anything**, including when
   CitizenPac runs into a Ghost.  AKA the game is in "debug mode."

   - The game will *never* end until you close the window, since there is no Food to
     complete eating, and you will never lose lives.

2. When you set this to ``True``, the food will be created **and** collisions will now
   be processed.

3. Since the game is in "debug mode", the move direction you compute is going to be
   printed to the console for you with extra information about what the current move
   flags are and what direction that should be.

   This is not here for you to hard-code values, we reserve the right to change the
   values of the directions declared at the top of :class:`view.actors.Actor`.
'''

NUM_LIVES          = 3
''' The number of "lives" CitizenPac starts with. '''


NUM_GHOSTS         = 3
'''
How many ghosts to add to the map.  Directly related to the size of
:data:`constants.DISPERSION_RADIUS` -- if you ask for too many Ghosts, then the game
will be impossible to play.  Since the actors are distributed on a circle, if you ask
for more than the circle can fit without overlapping, CitizenPac will start the game
colliding with Ghosts!

You can set :data:`constants.FULL_GAME_MODE` to ``True`` if you want to create many actors
for some reason.
'''

DISPERSION_RADIUS  = 222.222
'''
CitizenPac and the Ghosts are dispersed on a circle centered at the origin.  This
constant controls how close / far away the actors will start from the origin.
'''

GAME_REFRESH_RATE  = 10
'''
If the game is running slowly, INCREASE the value of this constant in order to get.
This time is in terms of MILLISECONDS, and the **larger** the value, the **slower**
the game runs.  So if the game runs slowly, increase this constant.
'''
