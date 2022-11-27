import networktables 
import tensorflow as tf


class Networktables:
    def __init__(self):
        self.ntinst = networktables.NetworkTablesInstance.getDefault()
        self.ntinst.startClientTeam(8775) 