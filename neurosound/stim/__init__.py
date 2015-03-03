
def get_stimulus_editor(name):
    # abstract this more
    from neurosound.gui.stim.abstract_editor import AbstractEditorWidget
    from neurosound.gui.stim.stimulus_editor import StimulusEditor
    from neurosound.gui.stim.tuning_curve import TuningCurveEditor

    if name == StimulusEditor.name:
        return StimulusEditor
    elif name == TuningCurveEditor.name:
        return TuningCurveEditor
    else:
        return None