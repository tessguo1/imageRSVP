from psychopy import event, sound
import numpy as np
import string
from copy import deepcopy
import time

def drawResponses(responses,respStim,numCharsWanted,changeToUpperCase,drawBlanks):
    '''Draw the letters the user has entered
    drawBlanks is whether to show empty spaces with _, that's why numCharsWanted would be needed
    '''
    respStr = ''.join(responses) #converts list of characters (responses) into string
    #print 'responses=',responses,' respStr = ', respStr #debugOFF
    if changeToUpperCase:
        respStr = respStr.upper()
    if drawBlanks:
        blanksNeeded = numCharsWanted - len(respStr)
        respStr = respStr + '_'*blanksNeeded
    respStim.setText(respStr,log=False)
    respStim.draw(); 
        
def collectStringResponse(numCharsWanted,x,respPromptStim,respStim,acceptTextStim,fixation,myWin,
                                               clickSound,badKeySound,requireAcceptance,autopilot,changeToUpperCase,responseDebug=False): 
    '''respPromptStim should be a stimulus with a draw() method
    '''
    event.clearEvents() #clear the keyboard buffer
    respStim.setPos([x,0])
    drawBlanks = True
    expStop = False
    passThisTrial = False
    responses=[]
    numResponses = 0
    accepted = True
    if requireAcceptance: #require user to hit ENTER to finalize response
        accepted = False
    while not expStop and (numResponses < numCharsWanted or not accepted):
        noResponseYet = True
        thisResponse=''
        while noResponseYet: #loop until a valid key is hit
           if fixation is not None:
                fixation.draw()
           respPromptStim.draw()
           drawResponses(responses,respStim,numCharsWanted,changeToUpperCase,drawBlanks)
           myWin.flip()
           click =  False
           if autopilot: #need to wait otherwise dont have chance to press a key 
                for f in range(20): time.sleep(.01) #core.wait(1.0/60) #myWin.flip()
           keysPressed = event.getKeys()
           if changeToUpperCase:
                keysPressed = [key.upper() for key in keysPressed] #transform to uppercase
           else:
                keysPressed = [key for key in keysPressed] 
           if autopilot:
               noResponseYet = False
               numResponses = numCharsWanted
               if 'ESCAPE' in keysPressed:
                   expStop = True
           elif len(keysPressed) > 0:
                key = keysPressed[-1] #process only the last key, it being the most recent. In theory person could type more than one key between window flips, 
                #but that might be hard to handle.
                thisResponse = key
                if key.upper() in ['ESCAPE']:
                     expStop = True
                     noResponseYet = False
#                  if key in ['SPACE']: #observer opting out because think they moved their eyes
#                      passThisTrial = True
#                      noResponseYet = False
                elif key.upper() in string.ascii_letters:
                    noResponseYet = False
                    responses.append(thisResponse)
                    numResponses += 1 #not just using len(responses) because want to work even when autopilot, where thisResponse is null
                    click = True
                elif key.upper() in ['BACKSPACE','DELETE']:
                    if len(responses) >0:
                        responses.pop()
                        numResponses -= 1
                else: #invalid key pressed
                    badKeySound.play()

        if click and (click is not None):
            clickSound.play()
        drawResponses(responses,respStim,numCharsWanted,changeToUpperCase,drawBlanks)
        myWin.flip() #draw again, otherwise won't draw the last key
        
        if (numResponses == numCharsWanted) and requireAcceptance:  #ask participant to HIT ENTER TO ACCEPT
            waitingForAccept = True
            while waitingForAccept and not expStop:
                if fixation is not None:
                    fixation.draw()
                acceptTextStim.draw()
                respStim.draw()
                for key in event.getKeys():
                    if key.upper() in ['ESCAPE']:
                        expStop = True
                        #noResponseYet = False
                    elif key.upper() in ['ENTER','RETURN']:
                        waitingForAccept = False
                        accepted = True
                    elif key.upper() in ['BACKSPACE','DELETE']:
                        waitingForAccept = False
                        numResponses -= 1
                        responses.pop()
                        drawResponses(responses,respStim,numCharsWanted,changeToUpperCase,drawBlanks)
                        myWin.flip() #draw again, otherwise won't draw the last key
                myWin.flip() #end of waitingForAccept loop
          #end of waiting until response is finished, all keys and acceptance if required
          
    responsesAutopilot = np.array(   numCharsWanted*list([('A')])   )
    responses = [response.upper() for response in responses] 
    responses=np.array( responses )
    #print 'responses=', responses,' responsesAutopilot=', responsesAutopilot #debugOFF
    return expStop,passThisTrial,responses,responsesAutopilot
# #######End of function definition that collects responses!!!! #####################################

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
    msg = visual.TextStim(window, text='press a key\n<esc> to quit')
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
    numCharsWanted = 5
    respPromptStim.setText('Enter your ' + str(numCharsWanted) + '-character response')
    requireAcceptance = True
    x=-.2 #x offset relative to centre of screen
    changeToUpper = True
    expStop,passThisTrial,responses,responsesAutopilot = \
                collectStringResponse(numCharsWanted,x,respPromptStim,respStim,acceptTextStim,None,window,clickSound,badKeySound,requireAcceptance,autopilot,
                                                        changeToUpper, responseDebug=True)
    print('responses=',responses)
    print('expStop=',expStop,' passThisTrial=',passThisTrial,' responses=',responses, ' responsesAutopilot =', responsesAutopilot)
    print('Finished') 
