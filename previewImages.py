from psychopy import monitors, visual, event, data, logging, core, sound, gui
import  os

monitorwidth = 38.7 #monitor width in cm

folder =   "images/calmFiller/"
nImagesInFolder = 48
waitBlank = False
scrn=0
fullscr = False
widthPix= 800 #monitor width in pixels of Agosta
heightPix= 600 #800 #monitor height in pixels
monitorname = 'testmonitor'
waitBlank = False
viewdist = 57
allowGUI = False
units = 'deg'
bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist) #relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )

def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
myWin = openMyStimWindow()

for x in xrange(nImagesInFolder):
    fname = folder + str(x+1) + '.jpg'
    toDraw = visual.ImageStim(myWin, image=fname, pos=(0,0), size=(320,240), units='pix', autoLog=False)
    toDraw.draw()
    myWin.flip()
    event.waitKeys(keyList=['q'], timeStamped=False)
    