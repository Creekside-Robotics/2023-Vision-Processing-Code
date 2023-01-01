import math

import numpy as np

from ..utils import Box, Translation
from ..constants import GameField
from ..vision import DynamicObject
from .dynamic_field import DynamicField
from .tasks import GameTask


class FieldProcessing:
    def __init__(self, complete_field: DynamicField):
        """
        Creates a field processing objects, that processes the field to get an output.
        @param complete_field: Dynamic field object to process
        """
        self.game_field = complete_field
        self.last_task: GameTask = GameTask(DynamicObject.from_list(GameField.special_objects[0]), self.game_field.robot)
        self.previous_successful_task_type = ""
        self.tasks: list[GameTask] = []

    def update_tasks(self) -> None:
        """
        Updates as list of possible tasks stored inside the processing object
        @return: null
        """
        self.tasks = []
        self.tasks.append(self.last_task)

        for obj in self.game_field.objects:
            if (obj.object_name != "Red Robot") and (obj.object_name != "Blue Robot"):
                self.tasks.append(GameTask(obj, self.game_field.robot))
        self.tasks.extend(
            GameTask(DynamicObject.from_list(obj), self.game_field.robot) for obj in GameField.special_objects
        )

    def weight_history(self, task: GameTask) -> float:
        if self.previous_successful_task_type == task.dynamic_object.object_name:
            return 0
        else:
            return 1

    def weight_object_proximity(self, task: GameTask) -> float:
        weight = 1
        for obj in self.game_field.objects:
            if obj.object_name in ("Red Robot" or "Blue Robot"):
                weight *= 0.99 ** (
                    15
                    - abs(
                        obj.absolute_coordinates
                        - task.dynamic_object.absolute_coordinates
                    )
                )
            if obj.object_name == "Home Square":
                weight *= 1.05 ** (
                    15
                    - abs(
                        obj.absolute_coordinates
                        - task.dynamic_object.absolute_coordinates
                    )
                )
        return weight

    def weight_travel_time(self, task: GameTask) -> float:
        return 0.98 ** task.estimate_time()

    def weight_game_time(self, task: GameTask) -> float:
        if task.dynamic_object.object_name != "Endgame Square":
            return 0.5
        if task == self.game_field.game_time < 20:
            return 1
        else:
            return 0

    def weight_probability(self, task: GameTask) -> float:
        return task.dynamic_object.probability

    def weight_velocity(self, task: GameTask) -> float:
        velocity = math.sqrt(
            task.dynamic_object.velocity[0] ** 2 + task.dynamic_object.velocity[1] ** 2
        )
        return 0.95**velocity

    def weight_previous_id(self, task: GameTask) -> float:
        if self.last_task is None:
            return 1

        if task.id == self.last_task.id:
            return 1

        return 0.5

    def rank_tasks(self):
        """
        Ranks of the tasks using weighting algorithm
        @return: None
        """
        for task in self.tasks:
            task.rating = (
                self.weight_history(task)
                * self.weight_velocity(task)
                * self.weight_probability(task)
                * self.weight_previous_id(task)
                * self.weight_game_time(task)
                * self.weight_object_proximity(task)
                * self.weight_travel_time(task)
            )
        self.tasks = sorted(self.tasks, key=lambda x: x.rating)

    def generate_task(self) -> None:
        """
        Generates the highest ranking task
        @return:None
        """
        self.last_task = self.tasks[0]
        self.last_task.clean_key_points()
        self.generate_key_points(self.last_task)
        self.last_task.generate_spline(
            final_rot=GameField.special_task_rotations.get(
                self.last_task.dynamic_object.object_name
            )
        )

    def get_output(self):
        """
        Gets the output for the selected task
        @return: tuple (xVel, yVel, rotVel) - all floats
        """
        output = self.last_task.get_output(speed=GameField.robot_translational_speed)
        if self.last_task.is_done():
            self.last_task = None
        return output

    def generate_key_points(self, task: GameTask, resolution: float = 0.2):
        """
        Generates the key points within spline to complete a task
        @param task: Task passes that will be modified with new key points
        @param resolution: Distance between sample points used to create key points
        @return: None
        """
        total_dist = abs(task.key_points[-2] - task.key_points[-1])
        obstructions = self.get_obstructing_objects()

        dist_to_finish = total_dist
        step_counter = 1
        tracked_points = [task.key_points[0]]
        tracked_angular_changes = [None, None]

        while dist_to_finish > resolution:
            direction_unit_vector = (task.key_points[-1] - task.key_points[-2]) / abs(
                task.key_points[-2] - task.key_points[-1]
            )
            test_point = (
                direction_unit_vector * resolution * float(step_counter)
                + task.key_points[-1]
            )
            for obj in obstructions:
                if self.within_object(test_point, obj):
                    if isinstance(obj, DynamicObject):
                        tracked_points.insert(
                            0,
                            obj.absolute_coordinates.push_away(
                                test_point, obj.radius + self.game_field.robot.size
                            )[0],
                        )
                    if isinstance(obj, Box):
                        tracked_points.insert(
                            0,
                            obj.push_outside(test_point, self.game_field.robot.size)[0],
                        )
                    break
                tracked_points.append(test_point)
                break
            if step_counter > 3:
                tracked_angular_changes[0] = Translation.angle_between(
                    tracked_points[-3] - task.key_points[0],
                    tracked_points[-2] - task.key_points[0],
                )
                tracked_angular_changes[1] = Translation.angle_between(
                    tracked_points[-2] - task.key_points[0],
                    tracked_points[-1] - task.key_points[0],
                )
                if tracked_angular_changes[0] > 0 and tracked_angular_changes[1] < 0:
                    task.key_points.insert(-1, tracked_points[-2])
                    tracked_points = [task.key_points[-2]]
                    tracked_angular_changes = [None, None]
                    step_counter = 0
            step_counter += 1
            dist_to_finish = abs(tracked_points[-1] - task.key_points[-1])
            print(dist_to_finish)

        x = np.array([point.x for point in task.key_points])
        y = np.array([point.y for point in task.key_points])

        dist = np.sqrt((x[:-1] - x[1:]) ** 2 + (y[:-1] - y[1:]) ** 2)
        task.key_dist = np.concatenate(([0], dist.cumsum()))

    def within_object(self, point: Translation, obj: DynamicObject | Box) -> bool:
        """
        Returns whether the robot will be interfering with an object at a given point.
        @param point: Translational coordinates of the robot
        @param obj: Object that would be colliding
        @return: Boolean, whether there is interference
        """
        if isinstance(obj, DynamicObject):
            return abs(point - obj.absolute_coordinates) < (
                obj.radius + self.game_field.robot.size
            )
        if isinstance(obj, Box):
            return obj.is_inside(point, -self.game_field.robot.size)

    def get_obstructing_objects(self) -> list[DynamicObject | Box]:
        """
        gets objects that could be obstructing
        @return: obstructing objects
        """
        obstructing_objects: list[Box | DynamicObject] = []
        obstructing_objects.extend(GameField.dead_zones)
        for item in self.game_field.objects:
            if (
                item.object_name in ("Red Robot", "Blue Robot")
                and item.probability > 0.5
            ):
                obstructing_objects.append(item)
        return obstructing_objects

    def process_field(self):
        self.update_tasks()
        self.rank_tasks()
        self.generate_task()
