********
Protocol
********

Allows generation of predefined series of stimuli, with ability to automaticaly manipulate stimuli parameters through ranges of given values. Provides an interface for the construction of custom composite stimuli.

The central table is a list of the tests to be presented, in order. Above the table are some labels that display the current progress of a running protocol. At the bottom are different editors for creating/editing tests.

* To add a test, drag an editor type into the protocol list area

* To remove a test, right click and drag it to the trash icon

* To reorder a test, right click and drag it to the desired location

* To edit a test, double click anywhere in its row, an editor should pop up in its own window

Editor Types
============

Builder
-------
Components
^^^^^^^^^^
Construction Tool for creating composite stimuli. Components are arranged in tracks in the central area. The tracks allow the overlapping of components. The order of the tracks makes no difference to the end signal. The order of components in the tracks (left-right) does matter, and is temporal.

* To add a component, drag its label from the area on the right into the central area. Its editor will automatically pop up. To accept press enter to close using the x in the corner of the window.

* To remove a component, right click and drag it to the trash icon

* To reorder a component, right click and drag it to the desired location

* To edit a component, double click it

* To create space between components, add and interval of silence, from the components list

* The reps field represents how many repetitions of each unique stimulus will be presented (Batab sweeps).

* The *Preview Spectrogram* button will generate a spectrogram of the current components in the view.

* To accept, press the *ok* button or x in the corner of the window

* The info field is currently unused

Auto-Parameters
^^^^^^^^^^^^^^^
Autotest in Batlab. Click the arrow at the bottom of the editor to expand this section. This will place the editor into selection mode, which does not allow re-ordering or editing of components.

#. First, add a new auto-parameter by dragging the *add* label into the central table area.
#. Then you must first select at least one component for this parameter to affect. The selected component will highlight itself blue, when it is selected. You may select as many components as you want for a parameter, and they are toggled out of the selection by clicking them again.
#. Now select the type of parameter to manipulate by clicking the leftmost cell in the table, and selecting from the drop-down menu. This menu will only display available parameters for the component types you have in the selection. You may have different types of parameters in a single selection, and it will only display the parameters which these stimulus types have in common.
#. Enter the desired start, stop, and step increments. Hovering you mouse over these field should display the units. The units should also match the rest of the program, so If you are using frequency in kHz elsewhere, it will be in kHz here too. The number of steps this make will update in the last field. The number of steps is automatically determined, and cannot be edited.

* To remove a parameter, right click and drag it to the trash icon

* To reorder a parameter, right click and drag it to the desired location

* You can add as many auto-parameters as desired, they will combine and loop through in the order listed. E.g. If you have a range of 5 frequency changes, followed by 3 Intensity changes, the stimuli generated will present each frequency for the first intensity, then move on and present each frequency for the second intensity, and likewise for the third. Unless, you tick the randomize box, then the stimuli will be shuffled to be presented in a random order. This will change for repeat presentations of a test. Trace repetitions are always presented in succession.

* Notice that when you click the parameters the selections change in the component view to reflect which components belong to what parameter.

* If you enter a start value that is different from the value in the component(s) selected, it will automatically update in the main view.

* Collapse the Auto-parameter area to go back to component editor mode.

.. _tuning_curve:

Tuning Curve
------------
Creates tuning curve out of pure tones, by running through a series of frequency and intensity settings.

* Duration field is for tone duration

* Reps field is number of repetitions for each frequency-intensity combo (Batlab sweeps)

* Risefall field is the rise and fall value for the generated tone

This exact tuning curve can actually be created using the builder, this editor is a shortcut.