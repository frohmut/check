#!/usr/bin/python3
# coding: utf-8

import sys
import os
import tkinter as Tkinter
import random
import subprocess
import getpass
import time
import psutil


import cv2
import pygame.camera
import pygame.image

import gtts
import vlc

user = getpass.getuser()

testl = []
with open('/home/p/check/checks_' + user + '.txt') as f:
    for line in f:
        v = line.strip().split(";")
        testl.append(v)

class Check:

    def shuffle(self):
        self.tests = [ v for v in self.tests_orig]
        random.shuffle(self.tests)

    def __init__(self, testset):

        self._root = Tkinter.Tk()
        self.speak = True

        label = Tkinter.Label(text='Test')
        label.grid(row=0)

        # 'the_end' dient zum Anzeigen des Resultates nach dem letzten Test
        self.the_end = False

        self.test = Tkinter.Label()
        self.test.grid(row=1, column=0)

        # Vokabeln kopieren und mischen
        self.tests_orig = testset
        self.shuffle()
        self.current = self.tests.pop()

        self.entry = Tkinter.Entry()
        self.entry.grid(row=1, column=1)
        self.entry.bind('<Return>', lambda x: self.on_check())

        self.check = Tkinter.Button(text='Start')
        self.check.grid(row=2)
        self.check['command'] = self.on_check

        self.repeat = Tkinter.Button(text='Nochmal')
        self.repeat.grid(row=3)
        self.repeat['command'] = self.show_test

        self.max_check = 15
        self.min_correct = 10
        self.cnt_correct = 0
        self.cnt_q = -1

        self.first_answer = True

        done = str(self.cnt_q) + "/" + str(self.max_check) + "     " + str(self.cnt_correct) + "/" + str(self.min_correct)
        self.done = Tkinter.Label(text=done)
        self.done.grid(row=4, columns=3)

        self.info = Tkinter.Label(text='')
        self.info.grid(row=5, column=3)

        q = Tkinter.Button(text='Ende')
        q.grid(row=8, column=4)
        q['command'] = lambda: sys.exit(0)

        j = "Start-Test: " + time.strftime("%Y-%m-%d %H:%M", time.localtime())
        t = Tkinter.Label(text=j)
        t.grid(row=9, column=4)

    def check_face(self):

        # get snapshot

        cam.start()
        img = cam.get_image()
        cam.stop()
        fname = "check_" + user + "_" + time.strftime("%Y-%m-%d-%H_%M", time.localtime())
        pygame.image.save(img, fname + ".png")

        image = cv2.imread(fname + ".png")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags = cv2.CASCADE_SCALE_IMAGE
        )
        print("faces: " + str(len(faces)))
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imwrite(fname + "_faces.png", image)
        return len(faces) > 0

    def check_answer(self):
        if self.first_answer:
            ok = self.check_face()
            if ok:
                self.first_answer = False
            else:
                self.info['text'] = 'Bitte in die Kamera schauen'
                return True

        res = self.entry.get()
        if res == self.current[0]:
            self.info['text'] = res + ' war richtig'
            self.cnt_correct = self.cnt_correct + 1
            if self.speak:
                self.say(res, "en")
                self.say(" war richtig", "de")
        else:
            # self.tests.append(self.current)
            self.tests = [ self.current ] + self.tests
            self.min_correct = self.min_correct + 1
            self.info['text'] = '>' + res + '< war leider falsch. ' +\
                self.current[1] + ' = ' +\
                self.current[0]
            self._root.update()
            if self.speak:
                self.say("Leider falsch. Richtig wäre ", "de")
                self.say(self.current[0], "en")
                self.say("Weiter geht's.", "de")
        return False

    def say(self, texts, langs):
        fn = "check_speak.mp3"
        g = gtts.gTTS(text=texts, lang=langs, slow=False)
        g.save(fn)
        p = vlc.MediaPlayer(fn)
        p.play()
        played = False
        while True:
            if p.get_position() > 0:
                played = True
            if played and p.is_playing() == 0:
                break


    def show_test(self):
        self.test['text'] = self.current[1]
        self.check['text'] = 'Check'
        if self.speak:
            self.test['text'] = ''
            self.say(self.current[1], "de")

    def on_check(self):

        if self.the_end == True:
            self.check['text'] = 'Spielzeit'
            self.check['command'] = None
            self.entry.bind('<Return>', None)
            j = "Start-Spiel: " + time.strftime("%Y-%m-%d %H:%M", time.localtime())
            t = Tkinter.Label(text=j)
            t.grid(row=10, column=4)
            try:
                p = subprocess.Popen([ "unity" ])
            except Exception as e:
                sys.exit(0)
            return

        # Check der Antwort
        if self.cnt_q >= 0:
            repeat = self.check_answer()
            if repeat:
                return

        # Neuer Test
        self.cnt_q = self.cnt_q + 1
        self.entry.delete(0, Tkinter.END)
        if self.cnt_q >= self.max_check and self.cnt_correct >= self.min_correct:
            # OK, Testende
            self.the_end = True
            self.test['text'] = ""
            self.check['text'] = 'Weiter'
        elif len(self.tests) > 0:
            self.current = self.tests.pop()
            self.show_test()
        else:
            # Liste durch, aber noch zu wenige Vok richtig
            self.shuffle()
            self.current = self.tests.pop()
            self.show_test()


        done = str(self.cnt_q) + "/" + str(self.max_check) + "     " + str(self.cnt_correct) + "/" + str(self.min_correct)
        self.done['text'] = done

    def battery_check(self):
        b = psutil.sensors_battery()
        if b.power_plugged == False:
            minsleft = b.secsleft / 60.0
            if minsleft < 5.0:
                subprocess.Popen(['notify-send', "Batterie hält noch " + str(minsleft) + " Minuten" ])
        self._root.after(60 * 1000, self.battery_check)


    def mainloop(self):
        self.battery_check()
        Tkinter.mainloop()

# Create the haar cascade
cascPath = "/home/p/check/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
pygame.camera.init()
cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])

c = Check(testl)

c.mainloop()

pygame.camera.quit()

# root.withdraw()


