
#Alex Holcombe alex.holcombe@sydney.edu.au
#See the README.md for more information: https://github.com/alexholcombe/attentional-blink/blob/master/README.md
#git remote add origin https://github.com/alexholcombe/attentional-blink.git
from __future__ import print_function
from psychopy import monitors, visual, event, data, logging, core, sound, gui
import psychopy.info
import numpy as np
from math import atan, log, ceil
from copy import deepcopy
import time, sys, os, random
try:
    from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, createNoise, plotDataAndPsychometricCurve
except ImportError:
    print('Could not import from noiseStaircaseHelpers.py (you need that file to be in the same directory)')
try:
    import imageLineupResponse
except ImportError:
    print('Could not import imageLineupResponse.py (you need that file to be in the same directory)')

imageSz = (320,240)
lineupImagesNotInStream = False
descendingPsycho = True
tasks=['T1','T1T2','T2']; task = tasks[2]
#THINGS THAT COULD PREVENT SUCCESS ON A STRANGE MACHINE
#same screen or external screen? Set scrn=0 if one screen. scrn=1 means display stimulus on second screen.
#widthPix, heightPix
quitFinder = False #if checkRefreshEtc, quitFinder becomes True
autopilot=False
demo=False #False
exportImages= False #quits after one trial
subject='Hubert' #user is prompted to enter true subject name
if autopilot: subject='auto'
if os.path.isdir('.'+os.sep+'data'):
    dataDir='data'
else:
    print('"data" directory does not exist, so saving data in present working directory')
    dataDir='.'
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime())

showRefreshMisses=True #flicker fixation at refresh rate, to visualize if frames missed
feedback=True
autoLogging=False
if demo:
    refreshRate = 60.;  #100

threshCriterion = 0.58
bgColor = [-1,-1,-1] # [-1,-1,-1]
cueColor = [0.,0.,1.]
letterColor = [1.,1.,1.]
cueRadius = 6 #6 deg, as in Martini E2    Letters should have height of 2.5 deg

widthPix= 1600 #monitor width in pixels of Agosta
heightPix= 900 #800 #monitor height in pixels
monitorwidth = 38.7 #monitor width in cm
scrn=1 #0 to use main screen, 1 to use external screen connected to computer
fullscr=False #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
if demo: monitorwidth = 23#18.0
if exportImages:
    widthPix = 400; heightPix = 400
    monitorwidth = 13.0
    fullscr=False; scrn=0
if demo:    
    scrn=0; fullscr=False
    widthPix = 800; heightPix = 600
    monitorname='testMonitor'
    allowGUI = True
viewdist = 57. #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
print('pixelperdegree=',pixelperdegree)
    
# create a dialog from dictionary 
infoFirst = {  'Check refresh etc':False, 'Fullscreen (timing errors if not)': False, 'Screen refresh rate': 60 }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='RSVP experiment', 
    order=['Check refresh etc', 'Fullscreen (timing errors if not)','Screen refresh rate'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating'},
    #fixed=['Check refresh etc'])#this attribute can't be changed by the user
    )
if not OK.OK:
    print('User cancelled from dialog box'); core.quit()
checkRefreshEtc = infoFirst['Check refresh etc']
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']
if checkRefreshEtc:
    quitFinder = True 
if quitFinder:
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)

#letter size 2.5 deg
numImagesInStream = 10
numRespOptions = 4
numImagesToPresent = 10
SOAms =  150 
imageDurMs = 150 

ISIms = SOAms - imageDurMs
imageDurFrames = int( np.floor(imageDurMs / (1000./refreshRate)) )
cueDurFrames = imageDurFrames
ISIframes = int( np.floor(ISIms / (1000./refreshRate)) )
#have set ISIframes and letterDurFrames to integer that corresponds as close as possible to originally intended ms
rateInfo = 'total SOA=' + str(round(  (ISIframes + imageDurFrames)*1000./refreshRate, 2)) + ' or ' + str(ISIframes + imageDurFrames) + ' frames, comprising\n'
rateInfo+=  'ISIframes ='+str(ISIframes)+' or '+str(ISIframes*(1000./refreshRate))+' ms and imageDurFrames ='+str(imageDurFrames)+' or '+str(round( imageDurFrames*(1000./refreshRate), 2))+'ms'
logging.info(rateInfo); print(rateInfo)

trialDurFrames = int( numImagesToPresent*(ISIframes+imageDurFrames) ) #trial duration in frames

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
myWin = openMyStimWindow()
refreshMsg2 = ''
if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
    refreshRateWrong = False
else: #checkRefreshEtc
    runInfo = psychopy.info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    #print(runInfo)
    logging.info(runInfo)
    print('Finished runInfo- which assesses the refresh and processes of this computer') 
    #check screen refresh is what assuming it is ##############################################
    Hzs=list()
    myWin.flip(); myWin.flip();myWin.flip();myWin.flip();
    myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
    print('About to measure frame flips') 
    for i in range(50):
        myWin.flip()
        Hzs.append( myWin.fps() )  #varies wildly on successive runs!
    myWin.setRecordFrameIntervals(False)
    # end testing of screen refresh########################################################
    Hzs = np.array( Hzs );     Hz= np.median(Hzs)
    msPerFrame= 1000./Hz
    refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    myWinRes = myWin.size
    myWin.allowGUI =True
myWin.close() #have to close window to show dialog box

defaultNoiseLevel = 0.0 #
trialsPerCondition = 1 #default value
dlgLabelsOrdered = list()
myDlg = gui.Dlg(title="RSVP experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name (default="Hubert"):', 'Hubert', tip='or subject code')
    dlgLabelsOrdered.append('subject')
myDlg.addField('\tPercent noise dots=',  defaultNoiseLevel, tip=str(defaultNoiseLevel))
dlgLabelsOrdered.append('defaultNoiseLevel')
myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', trialsPerCondition, tip=str(trialsPerCondition))
dlgLabelsOrdered.append('trialsPerCondition')
pctCompletedBreak = 50
    
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)

if checkRefreshEtc and (not demo) and (myWinRes != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    myDlg.addText(msgWrongResolution, color='Red')
    logging.error(msgWrongResolution)
    print(msgWrongResolution)
myDlg.addText('Note: to abort press ESC at a trials response screen', color=[-1.,1.,-1.]) # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()

if myDlg.OK: #unpack information from dialogue box
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
   trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
   print('trialsPerCondition=',trialsPerCondition)
   logging.info('trialsPerCondition =',trialsPerCondition)
   defaultNoiseLevel = int (thisInfo[ dlgLabelsOrdered.index('defaultNoiseLevel') ])
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()
if not demo: 
    allowGUI = False

myWin = openMyStimWindow()
#set up output data file, log file,  copy of program code, and logging
infix = ''
fileName = os.path.join(dataDir, subject + '_' + infix+ timeAndDateStr)
if not demo and not exportImages:
    dataFile = open(fileName+'.txt', 'w')
    saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
    os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
    logFname = fileName+'.log'
    ppLogF = logging.LogFile(logFname, 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
if demo or exportImages: 
  dataFile = sys.stdout; logF = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.ERROR) #DEBUG means set  console to receive nearly all messges, INFO next level, EXP, DATA, WARNING and ERROR 

if fullscr and not demo and not exportImages:
    runInfo = psychopy.info.RunTimeInfo(
        # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
        #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
        #version="<your experiment version info>",
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=False, ## True means report on everything 
        userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        #randomSeed='set:42', ## a way to record, and optionally set, a random seed of type str for making reproducible random sequences
            ## None -> default 
            ## 'time' will use experimentRuntime.epoch as the value for the seed, different value each time the script is run
            ##'set:time' --> seed value is set to experimentRuntime.epoch, and initialized: random.seed(info['randomSeed'])
            ##'set:42' --> set & initialize to str('42'), and will give the same sequence of random.random() for all runs of the script
        )
    logging.info(runInfo)
logging.flush()

#create click sound for keyboard
try:
    click=sound.Sound('406__tictacshutup__click-1-d.wav')
except: #in case file missing, create inferiro click manually
    logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
    click=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)

if showRefreshMisses:
    fixSizePix = 32 #2.6  #make fixation bigger so flicker more conspicuous
else: fixSizePix = 32
fixColor = [1,1,1]
if exportImages: fixColor= [0,0,0]
fixatnNoiseTexture = np.round( np.random.rand(fixSizePix/4,fixSizePix/4) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation

fixation= visual.PatchStim(myWin, tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False)
fixationBlank= visual.PatchStim(myWin, tex= -1*fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=False) #reverse contrast
fixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(1,1,1),size=10,units='pix',autoLog=autoLogging)

respPromptStim = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
acceptTextStim = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
respStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=.16,units='norm',autoLog=autoLogging)
clickSound, badKeySound = imageLineupResponse.setupSoundsForResponse()
requireAcceptance = False
nextText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(0,.2),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
screenshot= False; screenshotDone = False
stimList = []

#SETTING THE CONDITIONS
possibleCue1positions =  np.array([2,3,4]) 
possibleCue2lags = np.array([2])
for cue1pos in possibleCue1positions:
   for cue2lag in possibleCue2lags:
      for critDistractorArousing in [True, False]:
          for otherItemsArousing in [True, False]:
                stimList.append( {'cue1pos':cue1pos, 'cue2lag':cue2lag, 'critDistractorArousing':critDistractorArousing, 'otherItemsArousing':otherItemsArousing } )
#Martini E2 and also AB experiments used 400 trials total, with breaks between every 100 trials

trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method
numRightWrongEachCuepos = np.zeros([ len(possibleCue1positions), 1 ]); #summary results to print out at end
numRightWrongEachCue2lag = np.zeros([ len(possibleCue2lags), 1 ]); #summary results to print out at end

logging.info( 'numtrials=' + str(trials.nTotal) + ' and each trialDurFrames='+str(trialDurFrames)+' or '+str(trialDurFrames*(1000./refreshRate))+ \
               ' ms' + '  task=' + task)

def numberToLetter(number): #0 = A, 25 = Z
    #if it's not really a letter, return @
    #if type(number) != type(5) and type(number) != type(np.array([3])[0]): #not an integer or numpy.int32
    #    return ('@')
    if number < 0 or number > 25:
        return ('@')
    else: #it's probably a letter
        try:
            return chr( ord('A')+number )
        except:
            return('@')

def letterToNumber(letter): #A = 0, Z = 25
    #if it's not really a letter, return -999
    #HOW CAN I GENERICALLY TEST FOR LENGTH. EVEN IN CASE OF A NUMBER THAT' SNOT PART OF AN ARRAY?
    try:
        #if len(letter) > 1:
        #    return (-999)
        if letter < 'A' or letter > 'Z':
            return (-999)
        else: #it's a letter
            return ord(letter)-ord('A')
    except:
        return (-999)

#print header for data file
print('critDistFname\ttargetFname\t',file=dataFile,end='')
for i in xrange(numImagesInStream-2):
    print('fillerImage',i,sep='',file=dataFile,end='\t')
for i in xrange(3):
    print('lineupImage',i,sep='',file=dataFile,end='\t')
print('experimentPhase\ttrialnum\tsubject\ttask\t',file=dataFile,end='')
if task=='T1' or task=='T2':
    numRespsWanted = 1
    print('critDistractorArousing\totherItemsArousing\tcue1pos\tcue2lag\t',file=dataFile,end='')
elif task=='T1T2':
    numRespsWanted = 2
print('noisePercent\t',end='',file=dataFile)

for i in range(numRespsWanted):
   dataFile.write('answerPos'+str(i)+'\t')   #have to use write to avoid ' ' between successive text, at least until Python 3
   dataFile.write('answer'+str(i)+'\t')
   dataFile.write('response'+str(i)+'\t')
   dataFile.write('correct'+str(i)+'\t')
print('timingBlips',file=dataFile)
#end of header

def  oneFrameOfStim( n,cue1pos,cue2lag,cue,imageSequence,cueDurFrames,imageDurFrames,ISIframes,cuesPos,
                                       noise,proportnNoise,allFieldCoords,numNoiseDots,
                                       fillerAndLineupImages, targetImage,  critDistImage): 
#defining a function to draw each frame of stim. So can call second time for tracking task response phase
  SOAframes = imageDurFrames+ISIframes
  cueFrames = cuesPos*SOAframes  #cuesPos is  variable
  imageN = int( np.floor(n/SOAframes) )
  if imageN >   numImagesInStream:
    print('ERROR asking for ',imageN, ' but only ',numImagesInStream,' desired in stream')

  frameOfThisImage = n % SOAframes #every SOAframes, new letter
  showImage = frameOfThisImage < imageDurFrames #if true, it's not time for the blank ISI.  it's still time to draw the letter
  thisImageIdx = imageN
  #print 'n=',n,' SOAframes=',SOAframes, ' letterDurFrames=', letterDurFrames, ' (n % SOAframes) =', (n % SOAframes)  #DEBUGOFF
  #so that any timing problems occur just as often for every frame, always draw the letter and the cue, but simply draw it in the bgColor when it's not meant to be on
  cue.setLineColor( bgColor )
  for cueFrame in cueFrames: #check whether it's time for any cue
      if n>=cueFrame and n<cueFrame+cueDurFrames:
         cue.setLineColor( cueColor )

  if showImage:
    if imageN == cue1pos:
        critDistImage.draw()
    elif imageN == cue1pos + cue2lag:
        targetImage.draw()
    else:
        if imageN > cue1pos:
            thisImageIdx -= 1  #critical distractor was drawn separately, doesn't count toward nth item to take out of the fillerandLineup
        if imageN> cue1pos+cue2lag:
            thisImageIdx -= 1  #target was drawn separately, doesn't count toward nth item to take out of the fillerandLineup
        fillerAndLineupImages[thisImageIdx].draw()
    #if/then statements for what item to draw
  else:
   pass

  cue.draw()
  refreshNoise = False #Not recommended because takes longer than a frame, even to shuffle apparently. Or may be setXYs step
  if proportnNoise>0 and refreshNoise: 
    if frameOfThisImage ==0: 
        np.random.shuffle(allFieldCoords) 
        dotCoords = allFieldCoords[0:numNoiseDots]
        noise.setXYs(dotCoords)
  if proportnNoise>0:
    noise.draw()
  return True 
# #######End of function definition that displays the stimuli!!!! #####################################
#############################################################################################################################

cue = visual.Rect(myWin, 
                 width=324,
                 height=244,
                 lineColorSpace = 'rgb',
                 lineColor=cueColor,
                 lineWidth=30.0, #in pixels
                 units = 'pix',
                 fillColor=None, #beware, with convex shapes fill colors don't work
                 pos= [0,0], #the anchor (rotation and vertices are position with respect to this)
                 interpolate=True,
                 autoLog=False)#this stim changes too much for autologging to be useful

#predraw all images needed for this trial
imageHeight = 240; imageWidth = 320


#populated with 0s when the drawImages... function is called the first time. 
#Represents the number of times an image has been used. Position in the list represents image identity, which is numeric
calmCritDistUsage = np.array([])
calmTargetUsage = np.array([])
calmFillerUsage = np.array([])
arousCritDistUsage = np.array([])
arousTargetUsage = np.array([])
arousFillerUsage = np.array([])


def drawImagesNeededForThisTrial(numImagesInStream,numRespOptions,thisTrial):
    fillerAndLineupImages = list();     fillerAndLineupImageNames = list()
    #6 folders
    #arousing/non-arousing x critDistr,target,filler
    folders = [  ["calmCritDist","calmTarget","calmFiller"] ,
                      ["arousCritDist","arousTarget","arousFiller"] ]
    #target folder has 48 target images
    #distractor folder has 48 distractors
    #filler folder has 150 fillers
    nImagesInFolder = 48
    nImagesInFolderFillers = 150
    
    global calmCritDistUsage
    print(calmCritDistUsage)
    global calmTargetUsage
    print(calmTargetUsage)
    global calmFillerUsage
    #print(calmFillerUsage)
    global arousCritDistUsage
    print(arousCritDistUsage)
    global arousTargetUsage
    print(arousTargetUsage)
    global arousFillerUsage
    #print(arousFillerUsage)
    
    #first time this is called, set up lists of 0s
    if len(calmCritDistUsage) == 0 : calmCritDistUsage = np.array([0 for k in range(nImagesInFolder)])
    if len(calmTargetUsage) == 0 : calmTargetUsage = np.array([0 for k in range(nImagesInFolder)])
    if len(calmFillerUsage) == 0 : calmFillerUsage = np.array([0 for k in range(nImagesInFolderFillers)])

    if len(arousCritDistUsage) == 0 : arousCritDistUsage = np.array([0 for k in range(nImagesInFolder)])
    if len(arousTargetUsage) == 0 : arousTargetUsage = np.array([0 for k in range(nImagesInFolder)])
    if len(arousFillerUsage) == 0 : arousFillerUsage = np.array([0 for k in range(nImagesInFolderFillers)])

    #draw the filler items. also the lineup items, as they are from same folder as the filler items
    arousFolderIdx = thisTrial['otherItemsArousing']
    folderIdx = 2
    folder = folders[arousFolderIdx][folderIdx]
    if lineupImagesNotInStream:
        numImages = numImagesInStream-2 + numRespOptions-1
    else:
        numImages = numImagesInStream-2 
    imageNumList = np.arange(1,nImagesInFolderFillers+1)
    np.random.shuffle(imageNumList)
    imageNumList = imageNumList[0:numImages]
    for imageNum in imageNumList: #plus numRespOptions because need additional ones for the lineup
       if folder == 'calmFiller':
            # if calmFillerUsage[imageNum-1]==2:
            #     newImageNum = np.random.choice([i for i in np.arange(1,nImagesInFolderFillers+1) if i not in imageNumList and calmFillerUsage[i-1]<2])
            #     #imageNumList[imageNumList.index(imageNum)] = newImageNum
            #     imageNumList[np.where(imageNumList==imageNum)] = newImageNum
            #     imageNum = newImageNum
            calmFillerUsage[imageNum-1] += 1
       elif folder == 'arousFiller':
       	    # if arousFillerUsage[imageNum-1]==2:
            #     newImageNum = np.random.choice([i for i in np.arange(1,nImagesInFolderFillers+1) if i not in imageNumList and arousFillerUsage[i-1]<2])
            #     #imageNumList[imageNumList.index(imageNum)] = newImageNum
            #     imageNumList[np.where(imageNumList==imageNum)] = newImageNum
            #     imageNum = newImageNum
            arousFillerUsage[imageNum-1] += 1
       imageFilename = os.path.join("images",folder)
       #print("imageFilename path=",imageFilename)
       imageFilename +=  '/'  + str( imageNum ) + '.jpg'
       #print('loading image ',imageFilename)
       image = visual.ImageStim(myWin, image=imageFilename, pos=(0,0), size=imageSz, units='pix',autoLog=autoLogging)
       fillerAndLineupImages.append(image)
       fillerAndLineupImageNames.append(imageNum)
    #draw the target, same arousal as the other items
    folderIdx = 1 #target
    folder = folders[arousFolderIdx][folderIdx]
    if folder == 'calmTarget':
        targetImageWhich = np.random.choice(np.arange(1,nImagesInFolder+1)[calmTargetUsage<2])
        calmTargetUsage[targetImageWhich-1] += 1
    elif folder == 'arousTarget':
    	targetImageWhich = np.random.choice(np.arange(1,nImagesInFolder+1)[arousTargetUsage<2])
        arousTargetUsage[targetImageWhich-1] += 1
    targetFilename = os.path.join("images",folder) + '/'  + str( targetImageWhich ) + '.jpg'
    print(targetImageWhich,'\t', end='', file=dataFile) #print target name to datafile

    #print('loading image ',targetFilename)
    targetImage = visual.ImageStim(myWin, image=targetFilename, pos=(0,0), size=imageSz, units='pix',autoLog=autoLogging)

    #draw the critical distractor
    arousFolderIdx = thisTrial['critDistractorArousing']
    folderIdx = 0 #target
    folder = folders[arousFolderIdx][folderIdx]
    if folder == 'calmCritDist':
        whichImage = np.random.choice(np.arange(1,nImagesInFolder+1)[calmCritDistUsage<2])
        calmCritDistUsage[whichImage-1] += 1
    elif folder == 'arousCritDist':
        whichImage = np.random.choice(np.arange(1,nImagesInFolder+1)[arousCritDistUsage<2])
        arousCritDistUsage[whichImage-1] += 1
    imageFilename = os.path.join("images",folder) + '/'  + str(whichImage) + '.jpg'
    print(whichImage,'\t', end='', file=dataFile) #print crit distractor to datafile

    critDistImage = visual.ImageStim(myWin, image=imageFilename, pos=(0,0), size=imageSz, units='pix',autoLog=autoLogging)

    return fillerAndLineupImages, fillerAndLineupImageNames, targetImage,critDistImage,targetImageWhich
   
#All noise dot coordinates ultimately in pixels, so can specify each dot is one pixel 
noiseFieldWidthDeg=imageHeight *1.0
noiseFieldWidthPix = int( round( noiseFieldWidthDeg*pixelperdegree ) )

def timingCheckAndLog(ts,trialN):
    #check for timing problems and log them
    #ts is a list of the times of the clock after each frame
    interframeIntervs = np.diff(ts)*1000
    #print '   interframe intervs were ',around(interframeIntervs,1) #DEBUGOFF
    frameTimeTolerance=.3 #proportion longer than refreshRate that will not count as a miss
    longFrameLimit = np.round(1000/refreshRate*(1.0+frameTimeTolerance),2)
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded 150% of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0 and (not demo):
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                logging.error( 'trialnum='+str(trialN)+' '+longFramesStr )
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:
                            flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    flankingAlso = np.array(flankingAlso)
                    flankingAlso = flankingAlso[np.negative(np.isnan(flankingAlso))]  #remove nan values
                    flankingAlso = flankingAlso.astype(np.integer) #cast as integers, so can use as subscripts
                    logging.info( 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) )  ) #because this is not an essential error message, as previous one already indicates error
                      #As INFO, at least it won't fill up the console when console set to WARNING or higher
    return numCasesInterframeLong
    #end timing check
    
trialClock = core.Clock()
numTrialsCorrect = 0; 
numTrialsApproxCorrect = 0;
numTrialsEachCorrect= np.zeros( numRespsWanted )
numTrialsEachApproxCorrect= np.zeros( numRespsWanted )
nTrialsCorrectT2eachLag = np.zeros(len(possibleCue2lags)); nTrialsEachLag = np.zeros(len(possibleCue2lags))
nTrialsApproxCorrectT2eachLag = np.zeros(len(possibleCue2lags));

def do_RSVP_stim(fillerAndLineupImages,imageSequence, targetImage,critDistImage,cue1pos, cue2lag, proportnNoise,trialN):
    #relies on  variables:
    #   logging, bgColor
    #
    cuesPos = [] #will contain the positions of all the cues (targets)
    if task=='T1':
        cuesPos.append(cue1pos)
    if task=='T1T2':
        cuesPos.append(cue1pos+cue2lag)
    if task == 'T2':
        cuesPos.append(cue1pos+cue2lag)

    cuesPos = np.array(cuesPos)
    correctAnswers = np.array( imageSequence[cuesPos] )
    noise = None; allFieldCoords=None; numNoiseDots=0
    if proportnNoise > 0: #generating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each image
        (noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,noiseFieldWidthPix, bgColor)

    preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I have consistent timing blip first time that draw ringInnerR for phantom contours
    cue.setLineColor(bgColor)
    preDrawStimToGreasePipeline.extend([cue])
    for stim in preDrawStimToGreasePipeline:
        stim.draw()
    myWin.flip(); myWin.flip()
    #end preparation of stimuli
    
    core.wait(.1);
    trialClock.reset()
    fixatnPeriodMin = 0.3
    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+fixatnPeriodMin)   *refreshRate)  #random interval between 800ms and 1.3s (changed when Fahed ran outer ring ident)
    ts = list(); #to store time of each drawing, to check whether skipped frames
    for i in range(fixatnPeriodFrames+20):  #prestim fixation interval
        #if i%4>=2 or demo or exportImages: #flicker fixation on and off at framerate to see when skip frame
        #      fixation.draw()
        #else: fixationBlank.draw()
        fixationPoint.draw()
        myWin.flip()  #end fixation interval
    #myWin.setRecordFrameIntervals(True);  #can't get it to stop detecting superlong frames
    t0 = trialClock.getTime()

    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
        worked = oneFrameOfStim( n,cue1pos,cue2lag,cue,imageSequence,cueDurFrames,imageDurFrames,ISIframes,cuesPos,
                                                     noise,proportnNoise,allFieldCoords,numNoiseDots,
                                                     fillerAndLineupImages, targetImage,  critDistImage) #draw image and possibly cue and noise on top
        if exportImages:
            myWin.getMovieFrame(buffer='back') #for later saving
            framesSaved +=1              
        myWin.flip()
        t=trialClock.getTime()-t0;  ts.append(t);
    #end of big stimulus loop
    myWin.setRecordFrameIntervals(False);

    if task=='T1' or task=='T2':
        respPromptStim.setText('Which image was circled?',log=False)
    elif task=='T1T2':
        respPromptStim.setText('Which two images were circled?',log=False)
    else: respPromptStim.setText('Error: unexpected task',log=False)
    postCueNumBlobsAway=-999 #doesn't apply to non-tracking and click tracking task
    return imageSequence,cuesPos,correctAnswers, ts  
    

def play_high_tone_correct_low_incorrect(correct, playIncorrect=True, passThisTrial=False):
    highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3, bits=8)
    low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3, bits=8)
    highA.setVolume(0.9)
    low.setVolume(1.0)
    if correct:
        highA.play()
    elif passThisTrial:
        high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08, bits=8)
        for i in range(2): 
            high.play();  low.play(); 
    elif playIncorrect: #incorrect
        low.play()

myMouse = event.Mouse()  #  will use myWin by default

expStop=False; framesSaved=0
nDoneMain = -1 #change to zero once start main part of experiment

noisePercent = defaultNoiseLevel
phasesMsg = 'Experiment will have '+str(trials.nTotal)+' trials. Letters will be drawn with superposed noise of' + "{:.2%}".format(defaultNoiseLevel)
print(phasesMsg); logging.info(phasesMsg)

#myWin= openMyStimWindow();    myWin.flip(); myWin.flip();myWin.flip();myWin.flip()
nDoneMain =0

placeholder = visual.TextStim(myWin, text='When you are ready,\nclick the mouse to start the experiment', alignHoriz='center')

while nDoneMain < trials.nTotal and expStop==False:
    if nDoneMain==0:
        placeholderNoResponse = True
        while placeholderNoResponse:
            placeholder.draw()
            myWin.flip()
            mouse1, mouse2, mouse3 = myMouse.getPressed()
            if mouse1 or mouse2 or mouse3:
                placeholderNoResponse = False
        msg='Starting experiment'
        logging.info(msg); print(msg)
    thisTrial = trials.next() #get a trial
    cue1pos = thisTrial['cue1pos']
    cue2lag = None
    if task=="T1T2" or task=="T2":
        cue2lag = thisTrial['cue2lag']
        
    fillerAndLineupImages, fillerAndLineupImageNames, targetImage,critDistImage,targetImageWhichN = drawImagesNeededForThisTrial(numImagesInStream,numRespOptions,thisTrial)
    imageSequence = np.arange(0,numImagesInStream-2) #not including the critical distractor and the target
    np.random.shuffle(imageSequence)
    #print out the filler image filenames, in order
    for i in xrange(len(fillerAndLineupImageNames)):
        imageIname = fillerAndLineupImageNames[  imageSequence[i] ]
        print(imageIname,'\t', end='', file=dataFile)
        
    letterSequence,cuesPos,correctAnswers,ts  = do_RSVP_stim(fillerAndLineupImages, imageSequence, targetImage,critDistImage,cue1pos, cue2lag, noisePercent/100.,nDoneMain)
    numCasesInterframeLong = timingCheckAndLog(ts,nDoneMain)
    
    responses = list(); responsesAutopilot = list();
    lineupImageIdxs = np.arange( numImagesInStream-2 )
    np.random.shuffle(lineupImageIdxs)
    lineupImageIdxs = lineupImageIdxs[:3]
    lineupImages = list()
    for i in xrange(3): #assign random sequence of lineup images and print lineup image fnames
        lineupImages.append(  fillerAndLineupImages[ lineupImageIdxs[i] ]  )
        print(fillerAndLineupImageNames[ lineupImageIdxs[i] ], end='\t', file=dataFile) #first thing printed on each line of dataFile
    
    #print('fillerAndLineupImages=',fillerAndLineupImages,' last 3 for lineup=',fillerAndLineupImages[-3:])
    #lineupImages = fillerAndLineupImages[-3:]
    expStop,responseQuadrant,targetQuadrant,autopilotQuadrant = imageLineupResponse.drawChoiceArrayAndCollectResponse(targetImage, lineupImages, clickSound,myMouse, myWin,imageSz, expStop)
    if autopilot:
        correct = (autopilotQuadrant == targetQuadrant)
    else:  correct = (responseQuadrant == targetQuadrant)
    print('expStop=',expStop,' responseQuadrant=',responseQuadrant, ' autopilotQuadrant =', autopilotQuadrant, 'correct = ',correct)
    
    if not expStop:
        print('main\t', end='', file=dataFile) #first thing printed on each line of dataFile
        print(nDoneMain,'\t', end='', file=dataFile)
        print(subject,'\t',task,'\t', end='', file=dataFile)
        print(thisTrial['critDistractorArousing'],'\t',thisTrial['otherItemsArousing'],'\t',cue1pos,'\t',cue2lag,'\t', round(noisePercent,3),'\t', end='', file=dataFile)    
        numTrialsCorrect += correct #so count -1 as 0
        if task=="T1T2" or task=="T2":
            cue2lagIdx = list(possibleCue2lags).index(cue2lag)
            nTrialsCorrectT2eachLag[cue2lagIdx] += correct
            nTrialsEachLag[cue2lagIdx] += 1
            
        if exportImages:  #catches one frame of response
             myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
             framesSaved +=1; core.wait(.1)
             myWin.saveMovieFrames('exported/frames.mov')  
             expStop=True
        core.wait(.1)
        if feedback: play_high_tone_correct_low_incorrect(correct, playIncorrect=False, passThisTrial=False)
        
        for i in range(len(cuesPos)): #print response stuff to dataFile
            #header was answerPos0, answer0, response0, correct0
            print(cuesPos[i],'\t', end='', file=dataFile)
        answerName = targetImageWhichN
        print(answerName, '\t', end='', file=dataFile) #answer0
        print(responseQuadrant, '\t', end='', file=dataFile) #response0
        print(correct, '\t', end='',file=dataFile)   #correct0
        print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile

        nDoneMain+=1
        
        dataFile.flush(); logging.flush()
        print('nDoneMain=', nDoneMain,' trials.nTotal=',trials.nTotal) #' trials.thisN=',trials.thisN
        if (trials.nTotal > 6 and nDoneMain > 2 and nDoneMain %
             ( trials.nTotal*pctCompletedBreak/100. ) ==1):  #dont modulus 0 because then will do it for last trial
                nextText.setText('Click the mouse to continue!')
                nextText.draw()
                progressMsg = 'Completed ' + str(nDoneMain) + ' of ' + str(trials.nTotal) + ' trials'
                NextRemindCountText.setText(progressMsg)
                NextRemindCountText.draw()
                myWin.flip() # myWin.flip(clearBuffer=True) 
                waiting=True
                while waiting:
                   if autopilot: break
                   elif expStop == True:break
                   mouse1, mouse2, mouse3 = myMouse.getPressed()
                   if mouse1 or mouse2 or mouse3:
                        waiting = False
                   for key in event.getKeys():      #check if pressed abort-type key
                         if key in ['ESCAPE']: 
                            waiting=False
                         if key in ['ESCAPE']:
                            expStop = False
                myWin.clearBuffer()
        core.wait(.2); time.sleep(.2)
        #end main trials loop
timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
msg = 'Finishing at '+timeAndDateStr
print(msg); logging.info(msg)
if expStop:
    msg = 'user aborted experiment on keypress with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.error(msg)

if (nDoneMain >0):
    print('Of ',nDoneMain,' trials, on ',numTrialsCorrect*1.0/nDoneMain*100., '% of all trials all targets reported exactly correct',sep='')
    if len(numTrialsEachCorrect) >1:
        print('T2 for each of the lags,',np.around(possibleCue2lags,0),': ', np.around(100*nTrialsCorrectT2eachLag / nTrialsEachLag,3), '%correct')

logging.flush(); dataFile.close()
myWin.close() #have to close window if want to show a plot
