Radio Delay Gui
==============================
## Who

This is a fork from the [Radio Delay](https://github.com/stevenryoung/RadioDelay) project by [Steven Young](stevenryoung@gmail.com)

## What

Python tool to delay radio (or any generic audio input)

![alt text](https://github.com/j-steve-martinez/RadioDelayGui/images/dadioDelayGui.png "Radio Delay Gui")

## When
Use it when you meet these requirements:

  [Python 2.7 (32-bit if using Windows)](https://www.python.org/download/releases/2.7.7/)

  [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/)

## Where

  Ubuntu
  
  Windows

## Why

I like to listen to sports but not the nation broadcasters.  While watching the SF Giants in the playoffs headed to the World Series, I would use a delay program for windows but its delay was capped at 30 seconds.  The SF Giants broadcast was getting close to 25 seconds delay so I decided it may be wise to find an alternative delay program. I found [Radio Delay](https://github.com/stevenryoung/RadioDelay) and decided to write a graphical user interface (GUI) using the original code as the base.

## How

RADIO >> AUDIO CABLE >> PC >> (OPTIONAL) AUDIO CABLE >> (OPTIONAL) SPEAKERS

Ubuntu:

  nohup ./radioDelayGui.pyw &

Windows

  Double click radioDelayGui.pyw
