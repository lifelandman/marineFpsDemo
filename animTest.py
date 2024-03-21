import direct.directbase.DirectStart
from panda3d.core import Character, LoaderOptions
modelP = loader.loadModel('models/player1', LoaderOptions(LoaderOptions.LF_search | LoaderOptions.LF_report_errors | LoaderOptions.LF_convert_skeleton))
model = modelP.node()
model = modelP.find("**/+Character").node()
if model.is_of_type(Character.getClassType()):
    modelP.ls()
    print(model.get_num_bundles())
else:
    print('was not character')
    modelP.ls()