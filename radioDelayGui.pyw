#!/usr/bin/python
#name           :radioDelayGui.pyw
#description    :A script to delay the audio input from a device such as a radio
#author         :J. Steve Martinez - j.steve.martinez@gmail.com
#date           :20141102
#version        :v.1    
#usage          :./radioDelayGui.pyw
#notes          :       
#Python         :2.7.6
#============================================================================
from Tkinter import *
import pyaudio
from multiprocessing import Process, Pipe
import os
import sys

SAMPLE_RATE = 44100
CHUNK = 2048
WIDTH = 2

class Gui:
    def __init__(self, master, endCommand, getCommand):
        # Set up the GUI
        self.button1 = Button(master, text='Quit', background="red", command=endCommand)
        self.button1.pack(side=LEFT)
        
        self.button2 = Button(master, text='Set Delay', background="green", command=getCommand)
        self.button2.pack(side=LEFT)
         
        value = StringVar()
        self.entry = Entry(master, textvariable=value)
        self.entry.pack(side=LEFT)
        value.set(.01)
        
        self.gui_msg = StringVar()
        self.msglabel = Label(master, textvariable=self.gui_msg)
        self.msglabel.pack(side=LEFT)

        self.gui_msg.set("Enter a value greater than zero (0)")

class AudioDelay:
    def __init__(self, master):
        #self.msg = ""
        self.master = master

        # Set up the GUI part
        self.gui = Gui(master, self.endApplication, self.getPconn1)

        #start the delay
        self.run()

    def delay_loop(self, channels=2, filename='default.wav', conn=[]):
    
        # Initialize PyAudio
        p = pyaudio.PyAudio()
    
        # Initialize Stream
        stream = p.open(format=p.get_format_from_width(WIDTH),
                        channels=channels,
                        rate=SAMPLE_RATE,
                        input=True,
                        output=True,
                        frames_per_buffer=CHUNK)
    
        # Establish some parameters
        bps = float(SAMPLE_RATE)/float(CHUNK) # blocks per second
        desireddelay = 5.0 # delay in seconds
        buffersecs = 300 # size of buffer in seconds
        
        # Create buffer
        bfflen = int(buffersecs*bps)
        buff = [ 0 for x in range(bfflen) ]
        
        # Establish initial buffer pointer
        widx = int(desireddelay*bps) # pointer to write position
        ridx = 0 # pointer to read position
        
        # Prewrite empty data to buffer to be read
        blocksize = len(stream.read(CHUNK))
        for tmp in range(bfflen):
            buff[tmp] = '0' * blocksize
    
        # Preload data into output to avoid stuttering during playback
        for tmp in range(5):
            stream.write('0'*blocksize,CHUNK)
    
        # Loop until program terminates
        while True:
            # Write output and read next input
            buff[widx] = stream.read(CHUNK)    
    
            try:
                stream.write(buff[ridx],CHUNK,exception_on_underflow=True)
            except IOError: # underflow, priming the output
                #print "Underflow Occured"
                stream.stop_stream()
                stream.close()
                stream = p.open(format=p.get_format_from_width(WIDTH),
                                channels=channels,
                                rate=SAMPLE_RATE,
                                input=True,
                                output=True,
                                frames_per_buffer=CHUNK)
                for i in range(5):
                    stream.write('0'*blocksize,CHUNK,exception_on_underflow=False)
            
            # Update write and read pointers
            widx += 1
            ridx += 1
            if widx == bfflen:
                widx = 0
            if ridx == bfflen:
                ridx = 0
            
            # Check for updated delay
            if conn.poll():
                desireddelay = conn.recv()
                if desireddelay >= 0:
                    ridx = int((widx - int(desireddelay*bps)) % bfflen)
                elif desireddelay < 0:
                    stream.stop_stream()
                    stream.close()
                    break
    

    def run(self):
        # Establish pipe for delay process
        self.pconn1, self.cconn1 = Pipe()
        self.p1 = Process(target=self.delay_loop, args=(2,'default.wav',self.cconn1))
        self.p1.start()
        
    def getPconn1(self):
        #update the delay
        self.inp = float(self.gui.entry.get())
        if self.inp > 0:
            self.pconn1.send(self.inp)
            self.gui.msglabel.configure(fg = "black")
        else:
            self.gui.msglabel.configure(fg = "red")

    def endApplication(self):
        #send the loop the exit call and clean up
        self.pconn1.send(-1)
        self.p1.join()
        sys.exit(1)

root = Tk()
KNBR = AudioDelay(master=root)
KNBR.master.title("Welcome to Radio Delay GUI")
root.mainloop()
root.withdraw()
