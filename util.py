
from math import cos, sin, atan2
import configparser
import os
from PIL import Image
class Util():
    def __init__(self, cfg):
        self.cfg = cfg

    def readConfig(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(os.getcwd() + '\\config.ini')
        configDict = dict(config._sections)
        for section in configDict.keys():
            for key in configDict[section].keys():
                if configDict[section][key] == 'True':
                    configDict[section][key] = True
                if configDict[section][key] == 'False':
                    configDict[section][key] = False
        print(configDict)
        return configDict


    def writeConfig(self, configDict):
        config = configparser.ConfigParser()
        config.optionxform = str
        for section in configDict.keys():
            config.add_section(section)
            for key in configDict[section].keys():
                config.set(section, key, str(configDict[section][key]))

            with open(os.getcwd() + '\\config.ini', 'w') as f:
                config.write(f)


    def animate(self, cycle, frames):
        if cycle < 5**len(frames) - 1:
            cycle += 1
        else:
            cycle = 0
        frame = frames[cycle%len(frames)]
        return cycle, frame


    def getAngle(self, x, y):
        return atan2(-y, x)


    def getDisplacement(self, oldx, oldy):
        gravity = 0.5  # placeholder
        # global startingpos  # x,y
        # global xvelocity
        # global yvelocity
        # global t
        # global monitorwidth
        # global ground
        if self.cfg.startingpos[0] > self.cfg.monitorwidth - self.cfg.windowsize[0]//2:
            self.cfg.startingpos = (self.cfg.monitorwidth - self.cfg.windowsize[0]//2, self.cfg.startingpos[1])

        x = self.cfg.startingpos[0] + self.cfg.xvelocity * self.cfg.t * cos(self.cfg.angle)
        y = self.cfg.startingpos[1] - self.cfg.yvelocity * self.cfg.t * sin(self.cfg.angle) + 0.5 * gravity * (self.cfg.t ** 2)

        self.cfg.t += 1
        if x < -10:  # left wall bounce
            if self.cfg.angle > 0:
                self.cfg.angle = 3.14 - self.cfg.angle
            else:
                self.cfg.angle = -3.14 + self.cfg.angle
            x = -10
            self.cfg.startingpos = (x, y)
            self.cfg.xvelocity *= 0.7
            self.cfg.yvelocity *= 0.7

            self.cfg.t = min(3, self.cfg.t // 2)
            x = self.cfg.startingpos[0] + self.cfg.xvelocity * self.cfg.t * cos(self.cfg.angle)
            y = self.cfg.startingpos[1] - self.cfg.yvelocity * self.cfg.t * sin(self.cfg.angle) + 0.5 * gravity * (self.cfg.t ** 2)

        if x >= self.cfg.monitorwidth - self.cfg.windowsize[0]//2:  # half of sprite width
            if self.cfg.angle > 0:
                self.cfg.angle = 3.14 - self.cfg.angle
            else:
                self.cfg.angle = -3.14 + self.cfg.angle
            x = self.cfg.monitorwidth - self.cfg.windowsize[0]//2 - 10
            self.cfg.startingpos = (x, y)
            self.cfg.xvelocity *= 0.7
            self.cfg.yvelocity *= 0.7
            self.cfg.t = min(3, self.cfg.t // 2)
            x = self.cfg.startingpos[0] + self.cfg.xvelocity * self.cfg.t * cos(self.cfg.angle)
            y = self.cfg.startingpos[1] - self.cfg.yvelocity * self.cfg.t * sin(self.cfg.angle) + 0.5 * gravity * (self.cfg.t ** 2)

        if y > self.cfg.ground:
            y = self.cfg.ground

        if y < -10000:  # anti yeet into space measure
            self.cfg.startingpos = (x, -100)
            self.cfg.t = 1
            self.cfg.angle = -3.14 / 2
        if y < -100:
            self.cfg.t += 2

        return (x, y)


    def getJumpHeight(self):  # x,y

        # a(x-h)^2+k
        # h = x
        # k = y
        k = self.cfg.cursorpos[1]
        h = self.cfg.cursorpos[0] - self.cfg.startingpos[0]
        a = -k / (h ** 2)
        t1 = self.cfg.t - k


        # jump to right
        if self.cfg.cursorpos[0] > self.cfg.startingpos[0]:
            if t1 < 0:
                x = h - (t1 / a) ** 0.5 + self.cfg.startingpos[0]
                y = t1 + k
                self.cfg.t += max(-t1 * 0.05, 1)
            else:
                t2 = k - self.cfg.t
                y = t2 + k
                x = h + (t2 / a) ** 0.5 + self.cfg.startingpos[0]
                self.cfg.t += max(-t2 * 0.025, 1)
        else:  # jump to left
            if t1 < 0:
                x = h + (t1 / a) ** 0.5 + self.cfg.startingpos[0]
                y = t1 + k
                self.cfg.t += max(-t1 * 0.05, 1)
            else:
                t2 = k - self.cfg.t
                y = t2 + k
                x = h - (t2 / a) ** 0.5 + self.cfg.startingpos[0]
                self.cfg.t += max(-t2 * 0.025, 1)

        # might need to add a constant based on starting position of randy
        # y = t+k
        # return coordinates
        # print(x,y)
        y = round(self.cfg.startingpos[1] - y)
        # global ground
        if y > self.cfg.ground:
            y = self.cfg.ground
        if x < -10:
            x = -10
        # global monitorwidth
        if x > self.cfg.monitorwidth :
            x = self.cfg.monitorwidth

        return (x, y)

    def find_duration(self, imgpath):
        img = Image.open(imgpath)
        img.seek(0)  # move to the start of the gif, frame 0
        tot_duration = 0
        # run a while loop to loop through the frames
        while True:
            try:
                frame_duration = img.info['duration']  # returns current frame duration in milli sec.
                tot_duration += frame_duration
                # now move to the next frame of the gif
                img.seek(img.tell() + 1)  # image.tell() = current frame
            except EOFError:
                return tot_duration  # this will return the tot_duration of the gif