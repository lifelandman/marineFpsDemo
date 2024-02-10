from setuptools import setup

setup(
    name='mn9mml-prototype',
    options={
        'build_apps': {
            # Build asteroids.exe as a GUI application
            'gui_apps': {
                'mn9mml-prototype': 'main.py',
            },

            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/lifelandPandadev/output.log',
            'log_append': False,

            # Specify which files are included with the distribution
            'include_patterns': [
                '**/*.jpg',
                '**/*.egg',
                '*.prc'
            ],
            'file_handlers': {
                '.egg': lambda x,y,z: None
            },
            
            'include_modules':{
                'mn9mml-prototype': ['direct.particles.ParticleManagerGlobal', 'direct.showbase.PhysicsManagerGlobal']
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