from .funcs import *
#from .sample.sampleTrampoline import sampleTrampoline

from direct.directnotify.DirectNotify import DirectNotify

class entityManager():
    
    entChecks = (("funcRotateAroundTarget", funcRotateAroundTarget, {"speed": "float", "target":"nodepath"}),#Tag to look for entity signification, entity class, and then any tags to pass as values.
                 ("healing", funcHealing, {"healAmnt" : "float",}),
                 ("ladder", funcLadder, {}),
     )
    hostEntChecks = (#This is for entities that only need to run on the host computer.
        ("funcDisableWeapons", funcDisableWeapons, {}),
        )
    

    def __init__(self):
        world = base.game_instance.world
        self.entities = []
        
        notify = DirectNotify().newCategory("Entity initialization")

        if not base.isHost:
            checks = entityManager.entChecks
        else: checks = entityManager.entChecks + entityManager.hostEntChecks

        for entCheck in checks:
            for np in world.find_all_matches("**/=" + entCheck[0]):
                params = {}
                for param in entCheck[2]:
                    if np.has_tag(param):
                        try:
                            val = np.get_tag(param)
                            valType = entCheck[2][param]
                            if valType == "float": val = float(val)
                            elif valType == "nodepath":
                                val = val.replace(" ", "_")
                                val = world.find("**/" + val)
                                if val.is_empty(): continue
                            del valType
                            params[param] = val
                        except:
                            print("error setting entity value")#TODO:: properly alert the user of the map error
                        
                try:      
                    #print(np.get_name())
                    entity = entCheck[1](name = np.get_name() + "_" +entCheck[0], np = np, **params)
                    self.entities.append(entity)
                except Exception as error:
                    notify.warning("failed entity initialization: " + str(error))
        #render.ls()
                
    def get_entity(self, entName):
        for ent in self.entities:
            if ent.name == entName:
                return ent
        return False
                

    def destroy(self):
        for entity in self.entities:
            entity.destroy()