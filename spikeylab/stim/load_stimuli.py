import imp, glob, os

from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent

# stim_files = glob.glob('types'+os.sep+'[a-zA-Z]*.py')
# print 'files', stim_files
# this = imp.load_source('this', stim_files[0])

# print 'this', type(this)

def get_stimuli_models():
    package_path = os.path.dirname(__file__)
    # package_name = os.path.basename(package_path)
    # print package_path, package_name

    mod = '.'.join(get_stimuli_models.__module__.split('.')[:-1])
    print 'mod', mod
    if len(mod) > 0:
        mod =  mod + '.'
    print 'FIXME: MODULE LOCATION HARD-CODED'
    # mod = 'spikeylab.stim.'

    stim_folder = os.path.join(package_path, 'types')

    module_files = glob.glob(stim_folder+os.sep+'[a-zA-Z]*.py')
    # print 'modules files', module_files
    module_names = [os.path.splitext(os.path.basename(x))[0] for x in module_files]

    module_paths = [mod+'types.'+x for x in module_names]
    # print 'module paths', module_paths
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
    get_stimuli_models()