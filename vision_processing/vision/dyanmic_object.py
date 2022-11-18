from vision_processing import Translation


class DynamicObject:
    def __init__(
        self,
        relative_coordinates: Translation,
        radius: float,
        velocity: tuple[float, float] = (0, 0),
        absolute_coordinates: Translation = (0, 0),
        probability: float = 1,
    ):
        """
        Class to represent a moving object on a field
        :param relative_coordinates: coordinates of the object relative to the robot
        :type relative_coordinates: Translation
        :param radius: radius of the object
        :type radius: float
        :param velocity: velocity of the object
        :type velocity: tuple[float, float]
        :param absolute_coordinates: coordinates of object relative to field
        :type absolute_coordinates: Translation
        :param probability: probability that object exists within the radius
        :type probability: float
        """
        self.relative_coordinates = relative_coordinates
        self.radius = radius
        self.velocity = velocity
        self.absolute_coordinates = absolute_coordinates
        self.probability = probability
