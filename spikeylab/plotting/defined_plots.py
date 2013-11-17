from spikeylab.plotting.plotz import BasicPlot

def plot_cal_curve(results_array, freqs, intensities, p):
    # plot calibration curve: frequency against resultant dB by
    # target dB
    curve_lines = []
    for idb in xrange(results_array.shape[1]):
        ydata = results_array[:,idb]
        curve_lines.append((freqs,ydata))
    calcurve_plot = BasicPlot(*curve_lines, parent=p)
    calcurve_plot.setWindowTitle(u"Calibration Curve")
    calcurve_plot.axs[0].set_xlabel(u"Frequency (Hz)")
    calcurve_plot.axs[0].set_ylabel(u"Recorded dB")
    # set the labels on the lines for the legend
    for iline, line in enumerate(calcurve_plot.axs[0].lines):
        line.set_label(intensities[iline])
    calcurve_plot.axs[0].legend()
    calcurve_plot.show()

