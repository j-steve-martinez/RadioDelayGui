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

class Gui:
    def __init__(self, master, audio):
        self.myParent = master
        self.audio = audio
        self.setGui()
        self.audio.run()

    def setGui(self):
        self.default = "Enter a value greater than zero (0):"
        self.error   = "Enter a NUMBER!"
        
        self.myParent.title("Radio Delay GUI")    

        # Set the default close
        self.myParent.protocol('WM_DELETE_WINDOW', self.endCommand)       

        self.myContainer1 = Frame(self.myParent)
        self.myContainer1.pack()

        button_width = 6

        button_padx = "2m"
        button_pady = "1m"

        buttons_frame_padx =  "3m"
        buttons_frame_pady =  "2m"
        buttons_frame_ipadx = "3m"
        buttons_frame_ipady = "1m"

        self.buttons_frame = Frame(self.myContainer1) 
        self.buttons_frame.pack(
            side=TOP,
            ipadx=buttons_frame_ipadx,
            ipady=buttons_frame_ipady,
            padx=buttons_frame_padx,
            pady=buttons_frame_pady,
            )

        self.top_frame = Frame(self.myContainer1)
        self.top_frame.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )

        self.bottom_frame = Frame(self.myContainer1,
            borderwidth=5,  
            relief=RIDGE,
            height=50,
            )

        self.bottom_frame.pack(
            side=TOP,
            fill=BOTH,
            expand=YES,
            )

        self.left_frame = Frame(self.top_frame, background="yellow",
            borderwidth=5,  
            relief=RIDGE,
            height=250,
            width=50,
            )
        self.left_frame.pack(
            side=LEFT,
            fill=BOTH,
            expand=YES,
            )

        self.right_frame = Frame(self.top_frame, background="tan",
            borderwidth=5,
            relief=RIDGE,
            width=250,
            )
        self.right_frame.pack(
            side=RIGHT,
            fill=BOTH,
            expand=YES,
            )

        self.button1 = Button(self.bottom_frame, command=self.getCommand)
        self.button1.configure(text="Set", background= "green")
        self.button1.configure(
            width=button_width,
            padx=button_padx,
            pady=button_pady
            )
        self.button1.pack(side=LEFT)
        self.button1.bind("<Return>", self.getEvent)

        self.button2 = Button(self.bottom_frame, command=self.endCommand)
        self.button2.configure(text="Quit", background="red")
        self.button2.configure(
            width=button_width,
            padx=button_padx,
            pady=button_pady
            )
        self.button2.pack(side=RIGHT)
        self.button2.bind("<Return>", self.endEvent)

        self.gui_msg = StringVar()
        self.msglabel = Label(self.buttons_frame, textvariable=self.gui_msg)
        self.msglabel.pack(side=LEFT)
        self.gui_msg.set(self.default)

        self.value = StringVar()
        self.entry = Entry(self.right_frame, textvariable=self.value)
        self.entry.configure(
            width=5,
            relief=RIDGE
            )
        self.entry.focus_force()
        self.entry.bind("<Return>", self.getEvent)
        self.entry.pack(side=LEFT, padx=5, pady=5, ipadx=5, ipady=5)
        self.value.set(float(5))
        
        self.slider = Scale(self.right_frame)
        self.slider.configure(
            background="tan",
            from_=float(0),
            to=float(60),
            resolution=.1,
            orient=HORIZONTAL
            )
        self.slider.bind("<ButtonRelease-1>", self.setEntry)
        self.slider.pack(side=LEFT, padx=5, ipady=5)
        self.slider.set(self.entry.get())

        self.lb_delay = Label(self.left_frame, text="Delay:", bg="yellow")
        self.lb_delay.pack(side=LEFT, ipady=5)        

        self.delay_value = StringVar()
        self.msglabel2 = Label(self.left_frame, textvariable=self.delay_value, bg="yellow")
        self.msglabel2.pack(side=LEFT, padx=5, ipady=5)
        self.delay_value.set(self.value.get())

    def setEntry(self, event):
        self.value.set(self.slider.get())

    def endEvent(self, event):
        self.endCommand()
        
    def endCommand(self):
        self.audio.endApplication()

    def getEvent(self, event):
        self.getCommand()
        
    def getCommand(self):
        self.val = self.entry.get()
        try:
            float(self.val)
        except ValueError:
            self.msglabel.configure(fg = "red")
            self.gui_msg.set(self.error)
            return

        self.slider.set(self.val)
        self.delay_value.set(self.val)
        self.inp = self.val
        if self.inp > 0:
            self.audio.setPconn1(self.inp)
            self.msglabel.configure(fg = "black")
            self.gui_msg.set(self.default)
        else:
            self.msglabel.configure(fg = "red")

class AudioDelay:
    def __init__(self):
        self.sample_rate = 44100
        self.chunk = 2048
        self.width = 2
        
    def delay_loop(self, channels=2, filename='default.wav', conn=[]):
    
        # Initialize PyAudio
        p = pyaudio.PyAudio()
    
        # Initialize Stream
        stream = p.open(format=p.get_format_from_width(self.width),
                        channels=channels,
                        rate=self.sample_rate,
                        input=True,
                        output=True,
                        frames_per_buffer=self.chunk)
    
        # Establish some parameters
        bps = float(self.sample_rate)/float(self.chunk) # blocks per second
        desireddelay = 5.0 # delay in seconds
        buffersecs = 300 # size of buffer in seconds
        
        # Create buffer
        bfflen = int(buffersecs*bps)
        buff = [ 0 for x in range(bfflen) ]
        
        # Establish initial buffer pointer
        widx = int(desireddelay*bps) # pointer to write position
        ridx = 0 # pointer to read position
        
        # Prewrite empty data to buffer to be read
        blocksize = len(stream.read(self.chunk))
        for tmp in range(bfflen):
            buff[tmp] = '0' * blocksize
    
        # Preload data into output to avoid stuttering during playback
        for tmp in range(5):
            stream.write('0'*blocksize,self.chunk)
    
        # Loop until program terminates
        while True:
            # Write output and read next input
            buff[widx] = stream.read(self.chunk)    
    
            try:
                stream.write(buff[ridx],self.chunk,exception_on_underflow=True)
            except IOError: # underflow, priming the output
                #print "Underflow Occured"
                stream.stop_stream()
                stream.close()
                stream = p.open(format=p.get_format_from_width(self.width),
                                channels=channels,
                                rate=self.sample_rate,
                                input=True,
                                output=True,
                                frames_per_buffer=self.chunk)
                for i in range(5):
                    stream.write('0'*blocksize,self.chunk,exception_on_underflow=False)
            
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
