import time

from ..constants import GameField
from ..utils import Translation, dynamic_object_counter


class DynamicObject:
    def __init__(
        self,
        relative_coordinates: Translation,
        radius: float,
        object_name,
        velocity: tuple[float, float] = (0, 0),
        absolute_coordinates: Translation = Translation(0, 0),
        probability: float = 1,
    ):
        """
        Class to represent a moving object on a field
        :param relative_coordinates: coordinates of the object reltive to the robot
        :type relative_coordinates: Translation
        :param radius: radius of the object
        :object_name
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
        self.object_name = object_name
        self.velocity = velocity
        self.absolute_coordinates = absolute_coordinates
        self.probability = probability

        self.id = dynamic_object_counter.next()
        self.timestamp = time.time()

    def predict(self, *, delay: float | None = None, when: float | None = None) -> Translation:
        """
        Predict the position of an object in the future.
        Choose either ``delay`` for X seconds in the future,
        or ``when`` for a prediction at a certain unix timestamp.
        If both are passed, a ValueError is raised.

        :param delay: How many seconds in the future to predict
        :type delay: float | None
        :param when: A unix timestamp to make the prediction for
        :type when: float | None
        :return: The prediction of the object's translation, based
        :rtype:
        """
        if delay and when:
            raise ValueError("You cannot pass both `delay` and `when` together!")

        if delay is None and when is None:
            raise ValueError("You must pass either `delay` or `when`!")


        _step = delay or (when - self.timestamp)

        return Translation(
            self.absolute_coordinates.x + self.velocity[0]*_step,
            self.absolute_coordinates.y + self.velocity[1]*_step,
        )

    def update(self, other: "DynamicObject | None" = None, timestamp: float| None = None) -> None:
        """
        Update a dynamic object with information from a newer one

        :param other: The object to update from
        :type other: DynamicObject | None
        :param timestamp: A timestamp to update the position from
        :type timestamp: float | None
        """
        if other:
            prediction = self.predict(when=other.timestamp)
            position = (prediction + other.absolute_coordinates) / 2

            velocity = (position - self.absolute_coordinates) / (
                other.timestamp - self.timestamp
            )

            self.velocity = velocity
            self.absolute_coordinates = position
            self.timestamp = other.timestamp

            self.probability = 1

        if timestamp:
            prediction = self.predict(when=timestamp)

            time_diff = timestamp - self.timestamp
            probability_decay = GameField.prediction_decay**time_diff

            self.absolute_coordinates = prediction
            self.probability *= probability_decay
