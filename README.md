# PianoEar: A simple ear training system

## Features

* using midi file as music source
* display a simple scaleable staff of current song
* display a virtual piano keyboard
* support real time playing notes highlight
* support real time playing keys highlight
* enable/disable midi tracks while playing
* play midis file by lossless high quality wav samples
* low latency and smooth sound playing. (with out any noise on MacOS)
* running on MacOS/Linux, maybe Windows

## requirements

* pygame
* pyglet
* 88x8 sound wav files, put in:

    data/Piano_Sounds/Grand-021-048.wav

  * 88 keys (value range: 21 ~ 108)
  * 8 level each key (value is 48, 60, 71, 82, 91, 100, 115, 127)

* midi files, put in:

    midi/

  support 2 level directory. All midi files will show as 2 level menu.
