import math

import numpy as np

from vision_processing import GameField, Translation, DynamicObject, Box
from vision_processing.decision_making.dynamic_field import DynamicField
from vision_processing.decision_making.tasks import GameTask


class FieldProcessing:
    last_task: GameTask | None = None
    previous_successful_task_type = ""
    tasks: list[GameTask] = []

    def __init__(self, complete_field: DynamicField):
        self.game_field = complete_field

    def update_tasks(self):
        self.tasks = []
        if self.last_task is not None:
            self.tasks.append(self.last_task)
        for obj in self.game_field.objects:
            if obj.object_name != "Red Robot" or "Blue Robot" and obj.id != self.last_task.get_id():
                self.tasks.append(GameTask(obj, self.game_field.robot))
        for obj in GameField.special_objects:
            self.tasks.append(GameTask(obj, self.game_field.robot))

    def weight_history(self, task: GameTask):
        if self.previous_successful_task_type == task.dynamic_object.object_name:
            return 0
        else:
            return 1

    def weight_object_proximity(self, task: GameTask):
        weight = 1
        for obj in self.game_field.objects:
            if obj.object_name == "Red Robot" or "Blue Robot":
                weight *= 0.99 ** (15 - abs(obj.absolute_coordinates - task.dynamic_object.absolute_coordinates))
            if obj.object_name == "Home Square":
                weight *= 1.05 ** (15 - abs(obj.absolute_coordinates - task.dynamic_object.absolute_coordinates))
        return weight

    def weight_travel_time(self, task: GameTask):
        return 0.98 ** task.estimate_time()

    def weight_game_time(self, task: GameTask):
        if task == self.game_field.game_time < 20 and task.dynamic_object.object_name == "Endgame Square":
            return 1
        elif task == self.game_field.game_time > 20 and task.dynamic_object.object_name == "Endgame Square":
            return 0
        else:
            return 0.5

    def weight_probability(self, task: GameTask):
        return task.dynamic_object.probability

    def weight_velocity(self, task: GameTask):
        velocity = math.sqrt(task.dynamic_object.velocity[0] ** 2 + task.dynamic_object.velocity[1] ** 2)
        return 0.95 ** velocity

    def weight_previous_id(self, task: GameTask):
        if self.last_task is None:
            return 1

        if task.get_id() == self.last_task.get_id():
            return 1

        return 0.5

    def rank_tasks(self):
        for task in self.tasks:
            task.rating = (
                    self.weight_history(task) *
                    self.weight_velocity(task) *
                    self.weight_probability(task) *
                    self.weight_previous_id(task) *
                    self.weight_game_time(task) *
                    self.weight_object_proximity(task) *
                    self.weight_travel_time(task)
            )
        self.tasks = sorted(self.tasks, key=lambda x: x.rating)

    def generate_task(self):
        self.last_task = self.tasks[0]
        self.last_task.clean_key_points()
        self.generate_key_points(self.last_task)
        self.last_task.generate_spline()

    def get_output(self):
        output = self.last_task.get_output(speed=GameField.robot_translational_speed)
        if self.last_task.is_done():
            self.last_task = None
        return output

    def generate_key_points(self, task: GameTask, resolution: float = 0.2):
        total_dist = abs(task.key_points[-1] - task.key_points[-2])
        obstructions = self.get_obstructing_objects()

        dist_to_finish = total_dist
        step_counter = 1
        tracked_points = [task.key_points[0]]
        tracked_angular_changes = [None, None]

        while dist_to_finish > resolution:
            direction_unit_vector = (task.key_points[-2] - task.key_points[-1]) / abs(
                task.key_points[-2] - task.key_points[-1])
            test_point = direction_unit_vector * resolution * float(step_counter) + task.key_points[-2]
            for obj in obstructions:
                if self.within_object(test_point, obj):
                    if type(obj) == DynamicObject:
                        tracked_points.insert(0, obj.absolute_coordinates.push_away(
                            test_point,
                            obj.radius + self.game_field.robot.size
                        )[0])
                    if type(obj) == Box:
                        tracked_points.insert(0, obj.push_outside(
                            test_point,
                            self.game_field.robot.size
                        )[0])
                    break
                tracked_points.insert(0, test_point)
                break
            if step_counter > 3:
                tracked_angular_changes[0] = Translation.angle_between(
                    tracked_points[0] - task.key_points[-2],
                    tracked_points[1] - task.key_points[-2]
                )
                tracked_angular_changes[1] = Translation.angle_between(
                    tracked_points[1] - task.key_points[-2],
                    tracked_points[2] - task.key_points[-2]
                )
                if tracked_angular_changes[0] > 0 and tracked_angular_changes[1] < 0:
                    task.key_points.insert(-1, tracked_points[1])
                    tracked_points = [task.key_points[-2]]
                    tracked_angular_changes = [None, None]
                    step_counter = 0
            step_counter += 1
            dist_to_finish = abs(tracked_points[-1] - task.key_points[-1])

        x = np.array([point.x for point in task.key_points])
        y = np.array([point.y for point in task.key_points])

        dist = np.sqrt((x[:-1] - x[1:]) ** 2 + (y[:-1] - y[1:]) ** 2)
        task.key_dist = np.concatenate(([0], dist.cumsum()))

    def within_object(self, point: Translation, obj: DynamicObject | Box):
        if type(obj) == DynamicObject:
            return abs(point - obj.absolute_coordinates) < (obj.radius + self.game_field.robot.size)
        if type(obj) == Box:
            return obj.is_inside(point, -self.game_field.robot.size)

    def get_obstructing_objects(self):
        obstructing_objects: list[Box | DynamicObject] = []
        obstructing_objects.extend(GameField.dead_zones)
        for item in self.game_field.objects:
            if (item.object_name == "Red Robot" or "Blue Robot") and item.probability > 0.5:
                obstructing_objects.append(item)
        return obstructing_objects
