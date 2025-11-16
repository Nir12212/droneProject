from model.dataModel import DataModel
from model.picturesModel import PictureModel
from model.streamModel import StreamModel


class DroneController:
    def __init__(self):
        self.data = DataModel()
        self.pictures = PictureModel()
        self.stream = StreamModel()

    # DATA
    def get_sensor_data(self):
        return self.data.fetch_data()

    # PICTURES
    def get_picture(self):
        return self.pictures.receive_picture()

    def list_pictures(self):
        return self.pictures.images

    # STREAM
    def start_stream(self, callback):
        self.stream.start_stream(callback)
