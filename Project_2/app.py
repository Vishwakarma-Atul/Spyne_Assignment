from ultralytics import YOLO
import os

from .utils import Classifier

class inferance:
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.classification_model = YOLO(os.path.join(self.path, "models/classifier/best.pt"))

    def predict(self, image):
        classifer = Classifier(model=self.classification_model)
        _class, _conf = classifer.get_result(image)
        return _class, _conf

if __name__ == "__main__":
    infr = inferance()
    result = infr.predict("your/image.jpeg")
    print(result)