from .audio import Microphone, AudioFolder
from .vision import Camera, ImageFolder
from .measurements import MeasurementsFile

# USE ENV VAR TO DISTINGUISH DEV / TEST / PROD???

# take common, easy resources and make easy to access...
# alternatively, abstract out the data flow...

# some ideas... make different sizes to ensure user handles this??
# images = waggle.data.test_images()
# video = waggle.data.test_video()
# audio = waggle.data.test_audio()
