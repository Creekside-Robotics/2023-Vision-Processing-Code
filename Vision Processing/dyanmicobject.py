
class DynamicObject:

    def __init__(self, relative_coordinates, radius, velocity=(0, 0), absolute_coordinates=(0, 0), probability=1):
        """
        Class to represent a moving object on a field
        :param relative_coordinates: coordinates of the object relative to the robot
        :param radius: radius of the object
        :param velocity: velocity of the object
        :param absolute_coordinates: coordinates of object relative to field
        :param probability: probability that object exists within the radius
        """
        self.relative_coordinates = relative_coordinates
        self.radius = radius
        self.velocity = velocity
        self.absolute_coordinates = absolute_coordinates
        self.probability = probability


