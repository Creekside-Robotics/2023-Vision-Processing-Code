import math

import cv2
import numpy as np
from typing import Tuple

from ..vision import DynamicObject
from ..constants import GameField
from ..utils import Translation, Box
from ..decision_making import FieldProcessing


class UserInterface:
    def __init__(self, field_processing: FieldProcessing):
        self.field_processing = field_processing
        self.conversion_ratio = 350 / self.field_processing.game_field.field_boundary.upper_limit.y

    def translation_to_pixel_coordinates(self, translation: Translation) -> Tuple[int, int]:
        return 350 - self.field_length_to_pixel_length(translation.y), 500 - self.field_length_to_pixel_length(translation.x)

    def field_length_to_pixel_length(self, length: float) -> int:
        return int(length * self.conversion_ratio)

    def draw_dynamic_object(self, field, dynamic_object: DynamicObject):
        color_map = {
            "Red Robot": (0, 0, 255),
            "Blue Robot": (255, 20, 20),
            "Ball": (0, 255, 255)
        }
        pixel_coordinates = self.translation_to_pixel_coordinates(
            dynamic_object.absolute_coordinates
        )
        pixel_radius = self.field_length_to_pixel_length(dynamic_object.radius)
        return cv2.circle(field, pixel_coordinates, 0, color_map.get(dynamic_object.object_name), thickness=pixel_radius*2)

    def draw_box(self, field, box: Box, color):
        return cv2.rectangle(
            field,
            self.translation_to_pixel_coordinates(box.lower_limit),
            self.translation_to_pixel_coordinates(box.upper_limit),
            color,
            thickness=20
        )

    def generate_field(self):
        field = self.generate_field_base()
        field = self.add_path(field)
        field = self.add_dynamic_objects(field)
        field = self.add_robot(field)
        field = self.add_boundaries(field)
        field = self.add_game_time(field)
        return field

    def generate_field_base(self):
        base = np.full(shape=[500, 350, 3], fill_value=(200, 200, 200), dtype=np.uint8)
        for bound in GameField.special_boundaries:
            base = self.draw_box(base, bound, (150, 150, 150))
        return base

    def add_path(self, base):
        robot_mode_is_manual = self.field_processing.game_field.communications.get_robot_mode() == "Manual"
        color = ((255, 0, 0), (120, 120, 120))[robot_mode_is_manual]

        for index, item in enumerate(self.field_processing.last_task.spline_points):
            if index == len(self.field_processing.last_task.spline_points) - 1:
                break
            base = cv2.line(
                base,
                self.translation_to_pixel_coordinates(item),
                self.translation_to_pixel_coordinates(self.field_processing.last_task.spline_points[index + 1]),
                color,
                10
            )
        return base

    def add_dynamic_objects(self, base):
        field = base
        for obj in self.field_processing.game_field.objects:
            field = self.draw_dynamic_object(field, obj)
        return field

    def add_robot(self, field):
        robot_radius = self.field_processing.game_field.robot.size
        robot_pose = self.field_processing.game_field.robot.pose
        center = self.translation_to_pixel_coordinates(robot_pose.translation)
        direction_endpoint = self.translation_to_pixel_coordinates(
            Translation(math.cos(robot_pose.rot) * robot_radius, math.sin(robot_pose.rot) * robot_radius)
            + robot_pose.translation
        )
        field = cv2.circle(field, center, 0, (0, 255, 0), thickness=self.field_length_to_pixel_length(robot_radius)*2)
        field = cv2.line(field, center, direction_endpoint, (0, 0, 0), 5)
        return field

    def add_boundaries(self, field):
        field = self.draw_box(field, self.field_processing.game_field.field_boundary, (50, 50, 50))
        for bound in GameField.dead_zones:
            field = self.draw_box(field, bound, (50, 50, 50))
        return field

    def add_game_time(self, field):
        time = self.field_processing.game_field.game_time
        field = cv2.rectangle(field, (0, 0), (100, 50), (0, 0, 0), thickness=-1)
        field = cv2.putText(field, f"{int(time)}", (5, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return field








