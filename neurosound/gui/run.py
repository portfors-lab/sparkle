import sys
import logging

from QtWrapper import QtCore, QtGui

from neurosound.gui.main_control import MainWindow
from neurosound.gui.dialogs import SavingDialog
from neurosound.tools.systools import get_free_mb, get_drives
from neurosound.resources import icons

def log_uncaught(*exc_info):
    logger = logging.getLogger('main')
    logger.error("Uncaught exception: ", exc_info=exc_info)

def main():
    # this is the entry point for the whole application
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(icons.windowicon())
    sys.excepthook = log_uncaught
    # check free drive space, issue warning if low
    drives = get_drives()
    low_space = []
    plenty_space = []
    for drive in drives:
        space = get_free_mb(drive)
        if space < 1024:
            low_space.append((drive, space))
        else:
            plenty_space.append((drive, space))
    if len(low_space) > 0:
        if len(plenty_space) > 0:
            msg = "Waring: At least one Hard disk has low free space:\n\nDrives with low space:\n"
            for drive in low_space:
                msg = msg + "{} : {} MB\n".format(drive[0], drive[1])
            msg = msg + "\nDrives with more space:\n"
            for drive in plenty_space:
                msg = msg + "{} : {} MB\n".format(drive[0], drive[1])
            msg = msg + "\nYou are advised to only save data to a drive with enough available space"
            QtGui.QMessageBox.warning(None, "Drive space low", msg)
        else:
            msg = "Waring: All Hard disks have low free space:\n\n"
            for drive in low_space:
                msg = msg + "{} : {} MB\n".format(drive[0], drive[1])
            msg = msg + "\nIt is recommended that you free up space on a drive before conducting experiments"
            QtGui.QMessageBox.warning(None, "Drive space low", msg)

    dlg = SavingDialog()
    if dlg.exec_():
        fname, fmode = dlg.getfile()
        myapp = MainWindow("controlinputs.json", datafile=fname, filemode=fmode)
        app.setActiveWindow(myapp)
        myapp.show()
        status = app.exec_()
    else:
        status = 0
        print 'canceled'
    dlg.deleteLater()
    sys.exit(status)

if __name__ == "__main__":
    main()