from setuptools import setup

setup(
    name='mn9mml-prototype',
    options={
        'build_apps': {

            'gui_apps': {
                'aqua shift alpha': 'main.py',
            },

            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/lifelandPandadev/output.log',
            'log_append': False,

            # Specify which files are included with the distribution
            'include_patterns': [
                '**/*.jpg',
                '**/*.egg',
                '**/*.prc',
                '**/*.wav',
                '**/*.frag',
                '**/*.vert'
            ],
            'exclude_patterns': {
                'models/maps/*'
            },
            
            'include_modules':{
                
                },
            

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'pandaegg'
            ],
            
            'platforms':[
                #'manylinux2010_i686',
                'win_amd64',
                ]
        }
    }
)