from __future__ import print_function
from psychopy import event, sound
import numpy as np
import string, math
from copy import deepcopy
import random, os

def drawResponses(responses,respStim,numCharsWanted,drawBlanks):
    '''Draw the letters the user has entered
    drawBlanks is whether to show empty spaces with _, that's why numCharsWanted would be needed
    '''
    respStr = ''.join(responses) #converts list of characters (responses) into string
    #print 'responses=',responses,' respStr = ', respStr #debugOFF
    if drawBlanks:
        blanksNeeded = numCharsWanted - len(respStr)
        respStr = respStr + '_'*blanksNeeded
    respStim.setText(respStr,log=False)
    respStim.draw(); 

def drawChoiceArrayAndCollectResponse(targetImage,lineupImages,clickSound,myMouse,myWin,imageSz,expStop):
    event.clearEvents()
    numInArray = len(lineupImages) + 1
    targetPos = random.randint(0, numInArray)
    lineupImages.insert(targetPos,targetImage)
    xPosRange = 2; yPosRange = 2
    coords =  np.array( [ [.5,.5],[-.5,.5],[-.5,-.5],[.5,-.5] ] ) #only works for 4 items in choice array
    spacingFactor = 0.2
    coords =  np.round( coords * imageSz[0] * (1+spacingFactor) )
    coords = coords.astype(int)
    print('numInArray=',numInArray)
    
    respondedYet = False
    for i in xrange(numInArray):
        x= coords[i][0]
        y = coords[i][1]
        lineupImages[i].setPos((x,y))
        lineupImages[i].draw()
        print("Drew ", i, " at ",x,y)
    myWin.flip()
        
    while not respondedYet:
        for key in event.getKeys():
            if key in ['escape','q']:
                respondedYet = True
                expStop = True
        mouse1, mouse2, mouse3 = myMouse.getPressed()

        if mouse1 or mouse2 or mouse3:
            respondedYet = True
            mouseX,mouseY = myMouse.getPos()
            #clickSound.play()

    if (expStop):
        return 1,0,1,1
        
    print('mouseX,mouseY=',mouseX,mouseY)
    #calculate angle of mouse click vector
    mouseAngle = math.atan2(mouseY,mouseX)/math.pi*180
    if mouseAngle < 0:
        mouseAngle += 360
    respQuadrant = int( (mouseAngle)/90 )
    autopilotQuadrant = 1
    targetQuadrant = targetPos
    print("mouseAngle = ",mouseAngle, 'respQuadrant =',respQuadrant, 'targetQuadrant = ',targetQuadrant)
    return expStop,respQuadrant,targetQuadrant,autopilotQuadrant
    
#llerAndLineupImages, targetImage,  critDistImage
def drawChoiceArrayAndCollectResponseWithFnames(targetFileName, foilPath,foilFileNameList,clickSound, myWin,expStop):
    event.clearEvents()
    foilFnames = list()
    numInArray = len(foilFileNameList) + 1
    for fname in foilFileNameList:
        foilFname = os.path.join(foilPath,fname)
        foilFname = foilFname + '.jpg'
        foilFnames.append(foilFname)
    print("foilFnames = '",foilFnames)
    targetPos = random.randint(0, numInArray)
    allFnames = foilFnames
    random.shuffle(allFnames)
    allFnames.insert(targetPos,targetFileName)
    xPosRange = 2; yPosRange = 2
    coords = [ [.5,.5],[-.5,.5],[-.5,-.5],[.5,-.5] ]  #only works for 4 items in choice array
    print('numInArray=',numInArray)
    
    respondedYet = False
    for i in xrange(numInArray):
        x= coords[i][0]
        y = coords[i][1]
        fname = allFnames[i]
        toDraw = visual.ImageStim(myWin, image=fname, pos=(x,y), size=(.7,.7), units='norm', autoLog=autoLogging)
        print("Drew ", fname, " at ",x,y)
        toDraw.draw()
    myWin.flip()
        
    while not respondedYet:
        for key in event.getKeys():
            if key in ['escape','q']:
                respondedYet = True
                expStop = True
        mouse1, mouse2, mouse3 = myMouse.getPressed()

        if mouse1 or mouse2 or mouse3:
            respondedYet = True
            mouseX,mouseY = myMouse.getPos()
            clickSound.play()

    if (expStop):
        return 1,0,1,1
        
    print('mouseX,mouseY=',mouseX,mouseY)
    #calculate angle of mouse click vector
    mouseAngle = math.atan2(mouseY,mouseX)/math.pi*180
    if mouseAngle < 0:
        mouseAngle += 360
    respQuadrant = math.floor((mouseAngle)/90)
    autopilotQuadrant = 1
    targetQuadrant = targetPos
    print("mouseAngle = ",mouseAngle, 'respQuadrant =',respQuadrant, 'targetQuadrant = ',targetQuadrant)
    return expStop,respQuadrant,targetQuadrant,autopilotQuadrant

def setupSoundsForResponse():
    fileName = '406__tictacshutup__click-1-d.wav'
    try:
        clickSound=sound.Sound(fileName)
    except:
        print('Could not load the desired click sound file, instead using manually created inferior click')
        try:
            clickSound=sound.Sound('D',octave=3, sampleRate=22050, secs=0.015, bits=8)
        except:
            clickSound = None
            print('Could not create a click sound for typing feedback')
    try:
        badKeySound = sound.Sound('A',octave=5, sampleRate=22050, secs=0.03, bits=8)
    except:
        badKeySound = None
        print('Could not create an invalid key sound for typing feedback')
        
    return clickSound, badKeySound

if __name__=='__main__':  #Running this file directly, must want to test functions in this file
    from psychopy import monitors, visual, event, data, logging, core, sound, gui
    window = visual.Window()
    msg = visual.TextStim(window, text='Click a photo \n<esc> to quit')
    msg.draw()
    window.flip()
    autoLogging=False
    autopilot = False
    #create click sound for keyboard

    clickSound, badKeySound = setupSoundsForResponse()
    respPromptStim = visual.TextStim(window,pos=(0, -.7),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    acceptTextStim = visual.TextStim(window,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
    acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
    respStim = visual.TextStim(window,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=.16,units='norm',autoLog=autoLogging)

    responseDebug=False; responses = list(); responsesAutopilot = list();
    numCharsWanted = 2
    respPromptStim.setText('Enter your ' + str(numCharsWanted) + '-character response')
    requireAcceptance = True
    targetFileName = 'images/2480.jpg'
    imagePath = 'images/'
    imageFileNameList = list(['1019','1022','1030'] ) #should be same length as number of distractors want to show
    myMouse = event.Mouse()  #  will use myWin by default
    expStop = False
    expStop,respQuadrant,targetQuadrant,autopilotQuadrant = drawChoiceArrayAndCollectResponseWithFnames(targetFileName, imagePath,imageFileNameList, clickSound, window, expStop)
    responseAutopilot = 1
    passThisTrial = False
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' respQuadrant=',respQuadrant, ' autopilotQuadrant =', autopilotQuadrant)
    print('Finished') 