import sys
import os
import time

from App import MainApp
from config import config


if __name__ == '__main__':
    impath = os.getcwd() + '\\cat_animation'
    config = config(impath)
    config.setSize(440, 440)

    app = MainApp(sys.argv, config)
    sys.exit(app.exec_())
