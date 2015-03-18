import glob, os

from sparkle.stim.abstract_component import AbstractStimulusComponent

def get_stimuli_models():
    """
    Returns all subclasses of AbstractStimulusComponent in python files,
    in this package
    """
    package_path = os.path.dirname(__file__)

    mod = '.'.join(get_stimuli_models.__module__.split('.'))
    if mod == '__main__':
        mod = ''
    else:
        mod = mod + '.'

    module_files = glob.glob(package_path+os.sep+'[a-zA-Z]*.py')
    module_names = [os.path.splitext(os.path.basename(x))[0] for x in module_files]

    module_paths = [mod+x for x in module_names]
    modules = [__import__(x, fromlist=['*']) for x in module_paths]
 
    stimuli = []
    for module in modules:
        for name, attr in module.__dict__.iteritems():
            #test if attr is subclass of AbstractStim
            if type(attr) == type and issubclass(attr, AbstractStimulusComponent):
                # print 'found subclass', name, '!!!'
                stimuli.append(attr)

    # print stimuli
    return stimuli

if __name__ == '__main__':
    print get_stimuli_models()