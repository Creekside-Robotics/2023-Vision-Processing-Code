import math
from scipy import interpolate

from vision_processing import GameField
from vision_processing.decision_making.dynamic_field import DynamicField
from vision_processing.decision_making.tasks import GameTask


class FieldProcessing:
    last_task: GameTask = None
    previous_successful_task_type = ""
    tasks: list[GameTask] = []

    def __init__(self, complete_field: DynamicField):
        self.game_field = complete_field

    def update_tasks(self):
        self.tasks = []
        for obj in self.game_field.objects:
            if obj.object_name != "Red Robot" or "Blue Robot":
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
                weight *= 1.02 ** (15 - abs(obj.absolute_coordinates - task.dynamic_object.absolute_coordinates))
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

