# OpenCV (Open computer vision) is the backend for this fantastic code.
import cv2 as cv
from ultralytics import YOLO
from ezauv.utils import LogLevel
import sys

from ezauv.hardware.sensor_interface import Sensor

"""
Camera's need to be figured out on thier own. Meaning that if you have multiple cameras, you'll need to figure out which camera is which.
CameraIndex is returned into cv's VideoCapture. This also means that you can specify a video file, not just a camera ID. This can be used for testing.

"""


class CameraObject(Sensor):
    def __init__(
        self,
        camera,
        DivsionFactor,
        framerate,
        UseModel,
        model,
    ):
        camera = cv.VideoCapture(self.CameraIndex)
        DivisionFactor = self.DivisionFactor
        UseModel = self.UseModel
        model = self.model

    def initialize(self) -> None:
        cv, set(cv.CAP_PROP_FPS, self.framerate)

        # If the user chooses to use DivisionFactor to reduce the camera resolution, floor divide the width and height
        if self.DivisionFactor > 1:
            self.camera.set(
                cv.CAP_PROP_FRAME_WIDTH,
                int(self.camera.get(cv.CAP_PROP_FRAME_WIDTH)) // self.DivisionFactor,
            )
            self.camera.set(
                cv.CAP_PROP_FRAME_HEIGHT,
                int(self.camera.get(cv.CAP_PROP_FRAME_HEIGHT)) // self.DivisionFactor,
            )
        else:
            self.log(
                "WARNING: DivisionFactor is set to 1. This will have a noticable preformace impact.",
                LogLevel=LogLevel.WARNING,
            )

        # This is much faster than the pervious code because frame() is run in a loop in the main code so we only check if the camera is working once.
        # It might seem wierd because the camera could theoreticly fail at any time but this is faster.
        ret, frame = self.camera.read()
        if not ret:
            self.log("ERROR: Can not read camera. The program will now exit.")
            sys.exit(1)

        # Load da model if there is one!
        # We should also find some way to check if the sub is under remote control and if it is then we can unload the model. Clogs needs to get on that RC!
        if self.UseModel:
            self.log(
                "Loading YOLO model. This will have a preformance impact. Will try to run on Hailo."
            )
            model = YOLO(str(self.model))
        else:
            self.log("Not using YOLO")

    def get_data(self) -> list:
        ret, frame = self.camera.read()
        results = self.model(frame)

        bouys = []

        for r in results:
            for box in r:
                cordz = box.xyxy[0].tolist()
                cordz = [int(i) for i in cordz]

                width_pix = cordz[2] - cordz[0]
                center = ((cordz[0] + cordz[2]) / 2, (cordz[1] + cordz[3]) / 2)

                class_index = int(box.cls[0])

                distence = 0  # implamented later
                angle = 0  # implamented later

                bouys.append(class_index, distence, angle)

        return bouys
