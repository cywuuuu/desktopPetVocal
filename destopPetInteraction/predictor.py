import os

from destopPetInteraction.language_model3 import ModelLanguage
from destopPetInteraction.speech_features import Spectrogram
from destopPetInteraction.speech_model import ModelSpeech
from destopPetInteraction.speech_model_zoo import SpeechModel251BN

from tensorflow.python.keras.backend import set_session
import tensorflow as tf

class Predictor():
    def __init__(self):
        self.sess = tf.Session()
        self.graph = tf.get_default_graph()
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        AUDIO_LENGTH = 1600
        AUDIO_FEATURE_LENGTH = 200
        CHANNELS = 1
        OUTPUT_SIZE = 1428
        sm251bn = SpeechModel251BN(
            input_shape=(AUDIO_LENGTH, AUDIO_FEATURE_LENGTH, CHANNELS),
            output_size=OUTPUT_SIZE
        )
        features = Spectrogram()
        self.model = ModelSpeech(sm251bn, features, max_label_length=64)
        set_session(self.sess)
        self.model.load_model('destopPetInteraction/save_models/' + sm251bn.get_model_name() + '.model.h5')
        print("model loaded ok")
        self.langmodel = ModelLanguage('destopPetInteraction/model_language')
        self.langmodel.load_model()


    def predictSingleStep(self):
        with self.graph.as_default():
            set_session(self.sess)
            res = self.model.recognize_speech_from_file('output.wav')
            print('results of speech models:\n', res)
            lang_in = res
            res1 = self.langmodel.pinyin_to_text(lang_in)
            print('final results of speech2text:\n', res1)
            return res1, res


