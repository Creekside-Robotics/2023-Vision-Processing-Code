import networktables 
import tensorflow as tf


class Networktables:
    def __init__(self):
        self.ntinst = networktables.NetworkTablesInstance.getDefault()
        self.ntinst.startClientTeam(8775) 
        
    def SETaprilTagPoseDataEntry(self, poseArray): 
        self.ntinst.getEntry("April Tag Pose Entry").setDoubleArray(poseArray)
    def GETkinematicsDataEntry(self, poseArray):
        self.ntinst.getEntry("Kinematics Data Entry").setDoubleArray(poseArray)
    def GETfusedPoseDataEntry(self, poseArray):
        self.ntinst.getEntry("Fused Pose Data Entry").setDoubleArray(poseArray)
    
    