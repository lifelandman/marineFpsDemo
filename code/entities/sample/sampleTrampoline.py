'''
Hello! This file is meant to be a short tutorial on how to use my subframework, and more specifically it's entity system.
This tutorial unfortunately does not go over the basics of panda3d, however should hopefully be completable without such knowledge.
regardless, the panda3d manual can be found at https://www.panda3d.org/.

The goal of this tutorial is to create an entity that launches players upwards when they step into it's area.
Following this, we'll look at how to add this entity to the list of entites that are checked for when loading a map.

Additionally, you can look under models/maps to find the sampleTrampolineMap blender source file.
This is included in the source code to demonstrate how to add tags (and thus entities) to nodepaths using my OmUlette Blender plugin,
which can be found here: https://github.com/lifelandman/omUlette or here: https://extensions.blender.org/add-ons/omulete/

To see an example of what this tutorial should look like when it's done, check out sampleTrampolineComp.py.
'''

#First things first, we need to import the npEnt base class, which all entities that exist in the scene graph inherit from.
#I'll go ahead and do this for you:
from ..npEnt import npEnt
#Here's something other things that need to be imported for later:
from direct.task import Task
from panda3d.core import BitMask32


#Now, we need to create a class inheriting from npEnt. I've done this for you as well.

class sampleTrampoline(npEnt):
    #A nice thing about the entity system is that base classes define behaviors that can be controlled simply by defining various class variables.

    #using npEnt as an example, the "npOursOverridable" and "skipAccept" variables control
    #whether an entity 'owns' any nodepath passed to it, and whether the entity even cares if it recieves geometry, respectively.

    #Let's go ahead and set these to True, and False respectively.


    #This entity obviously needs collisions, so set "accept collisions to True.


    #next up we need to define the variables that are used by entBase, the parent class of all entites. These are particularly useful,
    #although I can't explain them all here. Go check out entBase.py for more info.


    #Go ahead and assign a tuple to the variable "events". You'll put another tuple inside of that.
    #The second tuple will contain a string that defines the name of the event to look for, and then another string that containts the name of some function you want to be called.

    #We'll put something in this tuple later. for now, just remember the keyword "Mayonaise".

    #Now create another variable holding a tuple, but this time for the variable "tasks".

    #For this tuple, remember the keyword "Fried Chicken".

    #A quick note on the above tuples; unlike most member variables in python, entBase contains code that makes all entBase-originating member variables
    #persist even in child classes. I.E. if you define an event to be accepted in A, and B is a child of A, B will automatically accept that event, even if
    #it's not explicitly accepted in B's definition. If you want to negate this behavior, add the task/event name to the variable excludedInheritedBehavior.


    #Alright! Now it's time to start writing functions that define the behavior of our entity. I'll go ahead and create all the function declarations for you, so just follow the
    #comments inside of them.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)#<-Do you know what this is?
        #Entities don't work unless you make the above call in every init function. If you're unfamilliar with kwargs or super().__init__, you should look those up.

        #first up, we need to define some instance variables. I'll go ahead and do that for you:
        self._boostingPlayers = {}
        #You might need to put something below here later. There's no keyword, but if there were, it'd be "rice".


        #Below is some code to let players walk through this entity's colliders. Hopefully before long I'll move bitmask-setting behavior into npEnt.
        cNodePaths= self.np.find_all_matches("**/+CollisionNode")
        for cNodePath in cNodePaths:
            node = cNodePath.node()
            if node.get_solid(0).is_tangible():
                node.set_into_collide_mask(BitMask32(0b0011000))#Change bitmask so player bBox can collide
                
        if self.np.node().is_collision_node:
            self.np.node().set_into_collide_mask(BitMask32(0b0011000))

        #And that's all we need to do in the initialization function!
    #Next up is adding players to our dictionary.


    def start_boost(self, entry):
        #This function will get called whenever a player begins to collide with this entity.
        #Because this event is called by the panda3d collision system, a CollisionEntry is passed to this function. The CollisionEntry class is beyond the scope of this tutorial,
        #So I'll take care of everything related to that. However this is a good time to point out that event recieving funtions need to match the # of parameters passed to the event.

        #First things first, I'll go ahead and grab the player entity.
        player = entry.get_from_node_path().get_net_python_tag("entOwner")
        #Notice that I grab the python tag "entOwner"? All derivitaves of npEnt set the value of that tag to point to themselves, making non-determinstic entity interaction easier.
        #One other thing that the panda3d manual doesn't explain well; most tags (just np.set_tag()) can only point to a string. set_python_tag() allows for the value of a key to be a python object.


        #The only other bit of code that this function needs is to add the player to the _boostingPlayers dict we made earlier.
        #First, check if the player's not already in our dictionary:

        #Go ahead and use player as the key, then set the value to 0.

        #There's one more thing we need to do though, and thats add this function to this entity's event recievers. Remember the comment up there with the keyword "Mayonaise"?
        #Go ahead and add the following as an entry within the events tuple, then come back here:
        #("player-in-{name}", "start_boost")

        #Did you notice the {name} keyword in the above string? (Brackets included) by putting that in a event or task name, that keyword is substituted for an entity's name at runtime.
        #Normally entMgr handles naming entities, but if you're creating entities manually, they can be named with the name= argument at initialization.

    def boost_players(self, task):
        #In this function, we'll add a set velocity (adjusted for dt) to players, and then increment the number of seconds they've been affected by this entity.
        players_to_remove = []
        for player in self._boostingPlayers.keys():

            #First, we need to get the deltatime since the last frame.
            dt = globalClock.get_dt()

            #now, add the dt to the amount of time the player's been affacted by the entity, then set the equivalent value in the dictionary:
            newTime = 0#?

            if newTime >= 2:#If they've been on longer than 2 seconds, remove them from our list of entities.
                #You might need to change the indentation here.
                if newTime >= 4:#If they've been on longer than 4 seconds, remove them from our list of entities.
                    players_to_remove.append(player)
                #2.037 is a nice number. it could even be 1/27th of a second over 2!
            #CHALENGE:: The above code is wrong! How can you make it so we don't apply more than two seconds' worth of velocity before the player is removed?

            #You can put something here, if you'd like.

            player.velocity.add_z(110*dt)

        for player in players_to_remove:
            #maybe another line or two of code in here to solve the challenge?
            self._boostingPlayers.pop(player)

        return Task.cont#This tells panda3d to run this task again the next frame. Read the manual for more details.

    #Now go ahead and add the above task to the tasks variable with the below (commented) tuple. Remember the keyword "fried chicken"?
    #("{name}-boost-players", "boost_players"),


'''
Congratulations! With this, you should have a fully-functioning entity of your very own. To test it, go ahead to entMgr.py
and import this class. Then, add it to entMgr's entChecks variable with the following:
("sampleTrampoline", sampleTrampoline, {}),

Then, load up the map "sampleTrampolineMap.egg", and try out your work!


There are a few things I didn't go over in this rough tutorial, but I tried to keep omissions limited to only being for brevity.
For instance, this guide doesn't go over the networking aspects of entities.

Also, this tutorial DOES show somewhat how to add your entity to what gets checked for by entMgr, but I'm probably going to make a
better system in the future.

In any case, I hope I've at least removed some of the fear of working with a framework, and that you'll give Panda3D a try sometime!
'''