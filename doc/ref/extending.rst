Extending Spikeylab
===================

Adding New Stimulus Types
-------------------------

Subsclassing AbstractStimulusComponent
++++++++++++++++++++++++++++++++++++++

To add a new stimulus type to the application, there must be a component class to represent it. To create a new component class, create a sub-class of :class:`AbstractStimulusComponent<spikeylab.stim.abstract_component.AbstractStimulusComponent>`, re-implementing the `signal`, and optionally, `auto_details`, `loadState`, `stateDict`, and `verify` methods, and the `name`, `protocol`, and `explore` properties:

    * :meth:`signal<spikeylab.stim.abstract_component.AbstractStimulusComponent.signal>` : This is the function that gets called to actually output the stimulus. You can use the :meth:`amplitude<spikeylab.stim.abstract_component.AbstractStimulusComponent.amplitude>` function to calculate the amplitude of your signal, however you also need to adjust to get the RMS amplitude. You can do this by using the :func:`rms<spikeylab.tools.audiotools.rms>` function from the tools package. Multiply this result against your signal to get the RMS amplitude.

    * :meth:`auto_details<spikeylab.stim.abstract_component.AbstractStimulusComponent.auto_details>` : The result of this method is used to determine what internal values will be available to set by the user and be manipulated with the :class:`AutoParameterModel<spikeylab.stim.auto_parameter_model>`. By default, this will be duration, intensity, and risefall. This should be subclassed if you wish to add other values to this collection, or if you wish to remove any of the defaults. When adding new parameters to this dict, the name of the variable that you are refering to with a new entry should be the key of entry, preceeded by an underscore. E.g. if the variable inside your component class you are trying to change via auto parameters is called `_foo`, then the entry in the `auto_details` should be something like this : :code:`'foo' : {'label': 'units', 'multiplier':1, 'min':1, max:5}`

    * :meth:`stateDict<spikeylab.stim.abstract_component.AbstractStimulusComponent.stateDict>` : Provides internal values to save for loading later. Allows for saving and loading of stimulus templates and propagating default values when adding a new component. The same keys of the values added to this dict should be used by `loadState` to assign to the saved values back to the appropriate variables. You should also add an extra field here, that is not used by `loadState`, which is `'stim_type'`. This field is used for documentation purposes.

    * :meth:`loadState<spikeylab.stim.abstract_component.AbstractStimulusComponent.loadState>` : Allows loading values from a previously saved component. Allows for saving and loading of stimulus templates and propagating default values when adding a new component. Assign the values in the provided dict to the internal variables that they were pulled from in `stateDict`

    * :meth:`verify<spikeylab.stim.abstract_component.AbstractStimulusComponent.verify>` : This method is called before a stimulus is generated (i.e before '`signal` is called), to check for errors. Check here for any disallowed values, or combination of values. e.g. that the risefall duration is not longer than the stimulus duration. This should return a useful error message of there is a conflict, or integer 0 for success.

    * :code:`name` : (`str`) this property will be the name that will show up on the GUI, and be in documentation, it should be unique from other Component classes

    * :code:`protocol` : (`bool`) whether this component class should be included as an option in the protocol builder portion of the GUI

    * :code:`explore` : (`bool`) whether this component class should be included as an option in the explore/search portion of the GUI

You are encouraged to look at examples of components in the :mod:`stimuli_classes<spikeylab.stim.types.stimuli_classes>` module. Add your own new classes to any module under the source folder *spikeylab/stim/types*, the application will look for any subclass of AbstractStimulusComponent in this package and pull it into the program. If you have set the protocol and/or explore properties set to `True` it should then automatically appear in the GUI.

Creating custom editors and visual representation
++++++++++++++++++++++++++++++++++++++++++++++++++

If you just do the above, then the new component will be added to the GUI using the default component editor and painted using a generic representation. To customize this, you must also subclass
:class:`QStimulusComponent<spikeylab.gui.stim.components.qcomponents.QStimulusComponent>`, and re-implement the `paint` and/or `showEditor` methods. The name of the new subclass should have the same name as your AbstractStimulusComponent subclass and pre-pended with a `Q`. This is important for the application to be able to find your custom GUI component subclass.