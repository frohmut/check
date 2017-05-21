#!/usr/bin/python3
# coding: utf-8

import sys
import os
import tkinter as Tkinter
import random
import subprocess
import getpass
import time

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

    def check_answer(self):
        res = self.entry.get()
        if res == self.current[0]:
            self.info['text'] = res + ' war richtig'
            self.cnt_correct = self.cnt_correct + 1
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
            self.say("Leider falsch. Richtig wäre ", "de")
            self.say(self.current[0], "en")
            self.say("Weiter geht's.", "de")

    def say(self, texts, langs):
        fn = "/tmp/test.mp3"
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
        self.test['text'] = ''
        self.check['text'] = 'Check'
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
            self.check_answer()

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
    def mainloop(self):
        self._root.mainloop()

c = Check(testl)

c.mainloop()


# root.withdraw()


