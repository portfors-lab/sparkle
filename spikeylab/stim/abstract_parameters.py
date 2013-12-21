from PyQt4 import QtGui

class AbstractParameterWidget(QtGui.QWidget):
    scales = [0.001, 1000] # time, frequency scaling factors
    funit_labels = []
    tunit_labels = []
    
    def setFScale(self, fscale):
        """
        Updates the frequency unit labels, and stores unit to
        to convert input before returning values in correct scale.
        """
        self.scales[1] = fscale
        if fscale == 1000:
            for lbl in self.funit_labels:
                lbl.setText('kHz')
        elif fscale == 1:
            for lbl in self.funit_labels:
                lbl.setText('Hz')
        else:
            raise Exception(u"Invalid frequency scale:"+str(self.fscale))

    def setTScale(self, tscale):
        """
        Updates the time unit labels, and stores unit to
        to convert input before returning values in correct scale.
        """
        self.scales[0] = tscale
        if tscale == 0.001:
            for lbl in self.tunit_labels:
                lbl.setText('ms')
        elif tscale == 1:
            for lbl in self.tunit_labels:
                lbl.setText('s')
        else:
            raise Exception(u"Invalid time scale:"+str(self.tscale))
            
    def inputsDict(self):
        return {}

    def loadInputsDict(self, inputs):
        pass

    def setComponent(self, component):
        raise NotImplementedError

    def saveToObject(self):
        raise NotImplementedError

class ParrotParameterWidget(AbstractParameterWidget):
    def changeTScale(self, n):
        self.tscale[0] = n

class RabbitParameterWidget(AbstractParameterWidget):
    pass

if __name__ == "__main__":

    parrot = ParrotParameterWidget()
    parrot2 = ParrotParameterWidget()
    rabbit = RabbitParameterWidget()

    print 'parrot start', parrot.tscale
    parrot.changeTScale(7)
    print 'and now', parrot.tscale, parrot2.tscale, rabbit.tscale
    rabbit.tscale.append(2)
    print 'and finally', parrot.tscale, parrot2.tscale, rabbit.tscale
    parrot.tscale = [5]
    print 'and finally', parrot.tscale, parrot2.tscale, rabbit.tscale
    rabbit.tscale.append(99)
    print 'and finally', parrot.tscale, parrot2.tscale, rabbit.tscale
    this = parrot2.tscale
    this.append('foo')
    print 'and finally', parrot.tscale, parrot2.tscale, rabbit.tscale
