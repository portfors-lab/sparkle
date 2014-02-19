
def get_stimulus_editor(name):
    # abstract this more
    from spikeylab.stim.abstract_editor import AbstractEditorWidget
    from spikeylab.stim.stimulus_editor import StimulusEditor
    from spikeylab.stim.tceditor import TuningCurveEditor

    if name == StimulusEditor.name:
        return StimulusEditor
    elif name == TuningCurveEditor.name:
        return TuningCurveEditor
    else:
        return None