import math

from ..constants import GameField
from ..utils import Pose, Translation, dynamic_object_counter


class DynamicObject:
    def __init__(
        self,
        relative_coordinates: Translation,
        radius: float,
        object_name,
        timestamp: float,
        velocity: Translation = Translation(0, 0),
        absolute_coordinates: Translation = Translation(0, 0),
        probability: float = 1
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
        self.timestamp = timestamp
        self.velocity_decay = 0.8
        self.velocity_frame_influence_factor = 0.8
        self.position_frame_influence_factor = 0.9

    @classmethod
    def from_list(cls, parameter_list: tuple) -> 'DynamicObject':
        """
        Returns a DynamicObject from a list of parameters to avoid circular import errors
        @param parameter_list: List of parameters: (
            relative_coordinates: Translation,
            radius: float,
            object_name,
            timestamp: float,
            absolute_coordinates: Translation = Translation(0, 0),
            object_id: int
        )
        @return: DynmaicObject
        """
        dynamic_object = cls(
            parameter_list[0],
            parameter_list[1],
            parameter_list[2],
            parameter_list[3],
            absolute_coordinates=parameter_list[4],
        )
        dynamic_object.id = parameter_list[5]

        return dynamic_object

    def predict(
        self, *, delay: float | None = None, when: float | None = None
    ) -> Translation:
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

        positional_change_factor = (self.velocity_decay**_step / math.log(self.velocity_decay, math.e)) - (1 / math.log(self.velocity_decay, math.e))
        positional_change = self.velocity * positional_change_factor

        return self.absolute_coordinates + positional_change


    def update(
        self, other: "DynamicObject | None" = None, timestamp: float | None = None
    ) -> None:
        """
        Update a dynamic object with information from a newer one

        :param other: The object to update from
        :type other: DynamicObject | None
        :param timestamp: A timestamp to update the position from
        :type timestamp: float | None
        """
        if other:
            prediction = self.predict(when=other.timestamp)
            new_velocity = (other.absolute_coordinates - self.absolute_coordinates) / (
                other.timestamp - self.timestamp
            )

            self.update_velocity(other.timestamp - self.timestamp, new_velocity)
            self.update_position(other.timestamp - self.timestamp, prediction)

            self.timestamp = other.timestamp

            self.probability = 1

        if timestamp:
            prediction = self.predict(when=timestamp)

            time_diff = timestamp - self.timestamp
            probability_decay = GameField.prediction_decay**time_diff

            self.timestamp = timestamp
            self.velocity *= self.velocity_decay**time_diff
            self.absolute_coordinates = prediction
            self.probability *= probability_decay

    def update_velocity(self, time_diff: float, new_velocity: Translation = Translation(0, 0)):
        update_influence = 1 - (1 - self.velocity_frame_influence_factor)**time_diff
        self.velocity = self.velocity * (1 - update_influence) + new_velocity * update_influence

    def update_position(self, time_diff: float, new_position: Translation):
        update_influence = 1 - (1 - self.position_frame_influence_factor) ** time_diff
        self.absolute_coordinates = self.absolute_coordinates * (1 - update_influence) + new_position * update_influence

    def add_absolute_coordinates(self, robot_pose: Pose) -> None:
        """
        Adds the absolute coordinates to DynamicObject
        @param robot_pose: The current pose of the robot
        @return: null
        """
        self.absolute_coordinates = self.relative_coordinates.relative_to_pose(robot_pose)
