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
    def __init__(self, master, audio):
        self.myParent = master
        self.audio = audio
        self.setGui()
        self.audio.run()

    def setGui(self):
        self.myParent.title("Welcome to Radio Delay GUI")    
        # Set the default close
        self.myParent.protocol('WM_DELETE_WINDOW', self.endCommand)
        
        # Setup the GUI 
        self.myContainer1 = Frame(self.myParent)
        self.myContainer1.pack(expand=YES, fill=BOTH)
        
        self.control_frame1 = Frame(self.myContainer1)
        self.control_frame1.pack(side=TOP, expand=NO, padx=10, pady=5, ipadx=5, ipady=5)      

        self.control_frame2 = Frame(self.myContainer1)
        self.control_frame2.pack(side=TOP, expand=NO, padx=10, pady=5, ipadx=5, ipady=5)

        self.button1 = Button(self.control_frame2, text='Quit', background="red", command=self.endCommand)
        self.button1.pack(side=LEFT)      
         
        value = StringVar()
        self.entry = Entry(self.control_frame2, textvariable=value)
        self.entry.config(width=5, relief=RIDGE)
        self.entry.focus_force()
        self.entry.pack(side=RIGHT, padx=5, pady=5, ipadx=5, ipady=5)
        value.set(5)
        
        self.button2 = Button(self.control_frame2, text='Set Delay', background="green", command=self.getCommand)
        self.button2.pack(side=RIGHT)
        
        self.gui_msg = StringVar()
        self.msglabel = Label(self.control_frame1, textvariable=self.gui_msg)
        self.msglabel.pack(side=LEFT)

        self.gui_msg.set("Enter a value greater than zero (0):")

    def endCommand(self):
        self.audio.endApplication()

    def getCommand(self):
        self.val = self.entry.get()
        self.inp = float(self.val)
        if self.inp > 0:
            self.audio.setPconn1(self.inp)
            self.msglabel.configure(fg = "black")
        else:
            self.msglabel.configure(fg = "red")

class AudioDelay:
    def __init__(self):
        self.msg = "_init_"

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
        
    def setPconn1(self, value):
        #update the delay
        self.pconn1.send(float(value))

    def endApplication(self):
        #send the loop the exit call and clean up
        self.pconn1.send(-1)
        self.p1.join()
        sys.exit(1)

if __name__ == '__main__':
    root = Tk()
    audio = AudioDelay()
    knbr = Gui(root, audio)
    root.mainloop()
