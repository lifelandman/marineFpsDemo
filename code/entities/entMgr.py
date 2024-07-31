from .funcs import funcRotateAroundTarget


class entityManager():
    
    entChecks = (("funcRotateAroundTarget", funcRotateAroundTarget, {"speed": "float", "target":"nodepath"}),#Tag to look for entity signification, entity class, and then any tags to pass as values.
     )
    

    def __init__(self):
        world = base.game_instance.world
        self.entities = []

        for entCheck in entityManager.entChecks:
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
                            print("entity value setting error")#TODO:: properly alert the user of the map error
                        
                try:      
                    entity = entCheck[1](name = np.get_name() + "_" +entCheck[0], np = np, **params)
                    self.entities.append(entity)
                except: print("failed entity initialization")
                
    def get_entity(self, entName):
        for ent in self.entities:
            if ent.name == entName:
                return ent
        return False
                

    def destroy(self):
        for entity in self.entities:
            entity.destroy()