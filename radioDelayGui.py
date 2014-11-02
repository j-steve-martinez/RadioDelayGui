from Tkinter import *
import pyaudio
from multiprocessing import Process, Pipe
import os
import sys
import time
import threading
import random
import Queue

DELAY_PROMPT = 'Enter your desired delay in seconds. Enter -1 to quit.\n'
SAMPLE_RATE = 44100
CHUNK = 2048
WIDTH = 2

COPYRIGHT = ('RadioDelay (aka Verne-Be-Gone)\n'
             'Copyright (C) 2014  Steven Young <stevenryoung@gmail.com>\n'
             'This program comes with ABSOLUTELY NO WARRANTY.\n'
             'This is free software, and you are welcome to redistribute it\n'
             'under certain conditions; type "show details" for more info\n')


class GuiPart:
    def __init__(self, master, queue, endCommand, getCommand):
        self.queue = queue
        # Set up the GUI
        self.button1 = Button(master, text='Quit', command=endCommand)
        self.button1.pack(side=RIGHT)
        
        self.button2 = Button(master, text='Set Delay', command=getCommand)
        self.button2.pack(side=RIGHT)
        self.button2.bind("<Return>", getCommand)

         
        # Add more GUI stuff here
        value = StringVar()
        self.entry = Entry(master, textvariable=value)
        self.entry.pack(side=LEFT)
        value.set(5)
        
        self.gui_msg = StringVar()
        self.msglabel = Label(master, textvariable=self.gui_msg, width=50, height=10)
        self.msglabel.pack(side=BOTTOM)

        self.gui_msg.set("Starting...")

    def getValue(self):
        self.value.get()
     

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.gui_msg.set(msg)
                #print msg
            except Queue.Empty:
                pass


class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master

        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.endApplication, self.getPconn1)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        #self.thread1 = threading.Thread(target=self.workerThread1)
        #self.thread1.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()
        
        #start the delay
        self.run()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            #import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following 2 lines with the real
            # thing.
            time.sleep(rand.random() * 0.3)
            msg = rand.random()
            self.queue.put(msg)

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
            
        print "Seconds per block: " + str(float(1/bps))
            
        # Write to command prompt
        self.write_terminal(desireddelay)
    
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
                print "Underflow Occured"
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
            #print "check update delay"
            if conn.poll():
                desireddelay = conn.recv()
                if desireddelay:
                    ridx = int((widx - int(desireddelay*bps)) % bfflen)
                    self.write_terminal(desireddelay)
                else:
                    stream.stop_stream()
                    stream.close()
                    break
    

    def run(self):
        # Establish pipe for delay process
        self.pconn1, self.cconn1 = Pipe()
        self.p1 = Process(target=self.delay_loop, args=(2,'default.wav',self.cconn1))
        self.p1.start()
        
        # Loop to check for change in desired delay
#        while True:
#            #self.inp = raw_input(DELAY_PROMPT) #set to gui input
#            #self.inp = self.gui.entry.get()
#            try:
#                #self.inp = float(inp)
#                self.inp = float(self.gui.entry.get())
#                if inp == -1.0: # Terminate
#                    self.pconn1.send(False)
#                    break
#                elif inp > 0.0: # Update delay
#                    self.pconn1.send(inp)
#                else:
#                    setMsg("Please use a delay longer than 0 sec.")
#            except:
#                if "show" in inp: # Give link to license
#                    setMsg("See the copy of GPLv3 provided with this program")
#                    setMsg("or <http://www.gnu.org/licenses/> for more details.")
#                else:
#                    setMsg("Improper input.")
#        #self.p1.join() #this ends the processing

    def getPconn1(self):
        self.inp = float(self.gui.entry.get())
        self.pconn1.send(self.inp)
    
    def setMsg(self, mgs):
        self.gui.gui_msg.set(msg)    

    def endApplication(self):
        self.p1.join() #this ends the processing
        self.running = 0

    def write_terminal(self, desireddelay):
        print desireddelay
        #os.system('cls' if os.name == 'nt' else 'clear')
        #print COPYRIGHT
        #print "Delay (seconds):", desireddelay
        #print DELAY_PROMPT

rand = random.Random()
root = Tk()

client = ThreadedClient(root)
client
root.mainloop()
