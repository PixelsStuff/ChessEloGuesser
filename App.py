import pandas as pd
import time
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import os 
import sys
import chess.pgn
import chess
import time
import statistics
from stockfish import Stockfish
import FreeSimpleGUI as sg
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
sg.theme('DarkGrey1')
def rff(fpath):
    with open(fpath) as f:
        return f.read()
def stf(fpath,epath,pgnpath):
    with open(fpath,'w') as f:
        return f.write(epath + '&THISPATHHERE-->' + pgnpath)

print()

FixData = True # ONLY USE THIS IF YOU ARE USING THE CSV PROVIDED 
infromationpath = 'GamesData.csv'
df = pd.read_csv(infromationpath,sep='|',header=None)
#pgn,evals,wacpl,white centipawn loss standard deviation,black centipawn loss standard deviation,numevals (serves as a sort of ply counter),welo,belo
if len(rff('savedsettings.txt').split('&THISPATHHERE-->')) > 1:
    tmesg = (rff('savedsettings.txt').split('&THISPATHHERE-->'))[1]
else:
    tmesg = ''
if len(rff('savedsettings.txt').split('&THISPATHHERE-->')) > 0:
    btmesg = (rff('savedsettings.txt').split('&THISPATHHERE-->'))[0]
else:
    btmesg = ''
layout = [
    [sg.Text('Stockfish Path')],
    [sg.Input(btmesg),sg.FileBrowse()],
    [sg.Text('PGN Path')],
    [sg.Input(tmesg),sg.FileBrowse()],
    [sg.Text('Engine Depth (18 reccomended)')],
    [sg.Input('18')],
    [sg.OK()]

]

window = sg.Window('Config',layout)#.read(close=True)
#print(event,values)
enginepath = ''
pgnpath = '' 
depth = 18
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED,'OK'):
        enginepath = values[0]
        pgnpath = values[1]
        depth = values[2]
        #print('hit')
        stockfishpath = enginepath
        stf('savedsettings.txt',enginepath,pgnpath)
        break
    if event in (sg.WIN_CLOSED,'cancel'):
        break
window.close()
'''
for i in range(1000):   # this is your "work loop" that you want to monitor
    meter = sg.one_line_progress_meter('One Line Meter Example', i + 1, 1000,'message','another')
    if not meter:
        break
    '''

stockfishpath = enginepath


eng = Stockfish(path=stockfishpath)
eng.set_depth(18) 
eng.set_turn_perspective(False)





numrows = 0

numrows = len(df)
print(numrows)
whitestd = []
blackstd = []
blackacpl = []
whiteacpl = []
kindaplycounter = []
welos = []
belos = []
for i in range(numrows): 
    whiteacpl.append(round(df.iloc[i,2]))
    whitestd.append(round(df.iloc[i,3]))
    blackacpl.append(round(df.iloc[i,4]))
    blackstd.append(round(df.iloc[i,5]))
    kindaplycounter.append(df.iloc[i,6])
    welos.append(df.iloc[i,7])
    belos.append(df.iloc[i,8])
#
#print(whiteacpl)

whitedata = {"WhiteACPL":whiteacpl,"WstdACPL":whitestd,"Moves":kindaplycounter,"BlackACPL":blackacpl,"BstdACPL":blackstd,"WhiteElo":welos,"BlackElo":belos}
wdataf = pd.DataFrame(whitedata)

if FixData:
    wdataf = wdataf.drop([6,7,8,9,116])


print(wdataf)
blackdata = {}
#print(welos)
#print(whiteacpl)
print(sum(kindaplycounter))
X = wdataf[["WhiteACPL","WstdACPL","Moves","BlackACPL","BstdACPL"]]
y = wdataf[["WhiteElo","BlackElo"]]

model = RandomForestRegressor(n_estimators=250)
X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.4,
    )




model.fit(X_train,y_train)
predictions = model.predict(X_test)
print(predictions)

error = mean_absolute_error(y_test, predictions)
print(error)
print()

print()
#print(whitedata)

#for index,row in wdataf.iterrows():
#    print(row[1:])
#    input()
# Duplicates on game 5 FOR 6 AND 7 AND 8 AND 9, PURE DUPE
# DUPLICATE ON 115 AND 116 [DELETE 116]

def processevals(evalslist): #Missed mates are evaluated as -1000 + min(eval of positon,800) of centipawn gain
    wcpl = []
    bcpl = []
    plylook = 0
    while len(evalslist) >= plylook+2:
      #  print('evalbefore',evalslist[plylook][1])
      #  print('evalafter',evalslist[plylook+1][1])
        if (evalslist[plylook][0] == False) and (evalslist[plylook+1][0] == False):
            n = max(evalslist[plylook][1] - evalslist[plylook+1][1],0)
            wcpl.append(n)
        elif (evalslist[plylook][0] == True) and (evalslist[plylook+1][0] == False):
            wcpl.append(min(1000-min(evalslist[plylook+1][0],900),1200))
        else:
            try:
                if evalslist[plylook][1]/abs(evalslist[plylook][1]) == evalslist[plylook+1][1]/abs(evalslist[plylook+1][1]):
                    pass #keeping acpl the same if nothing changes to prevent rewarding players for prolonging mate
                else:
                    wcpl.append(1400) #Two points extra because you suck if you went from +M1 to -M1
            except ZeroDivisionError:
                pass
             
        plylook += 2
    print(sum(wcpl)/len(wcpl))
    print(statistics.stdev(wcpl))
    print()
    plylook = 1
    while len(evalslist) >= plylook+2:
        #print(len(evalslist),plylook)
      ###  print('evalbefore',evalslist[plylook+0][1])
        #print('evalafter',evalslist[plylook+1][1])
        if (evalslist[plylook][0] == False) and (evalslist[plylook+1][0] == False):
            n = max(evalslist[plylook+1][1]-evalslist[plylook][1],0)
            bcpl.append(n)
        elif (evalslist[plylook][0] == True) and (evalslist[plylook+1][0] == False):
             bcpl.append(max(1000+(max(evalslist[plylook+1][1],-900)),1200))
        else:
            try:
             if evalslist[plylook][1]/abs(evalslist[plylook][1]) == evalslist[plylook+1][1]/abs(evalslist[plylook+1][1]):
                 pass
                #bcpl.append(0) k
             else:
                bcpl.append(1400) #Two points extra because you suck if you went from +M1 to -M1
            except ZeroDivisionError:
                pass
         #   print(n)
        plylook += 2
    print(sum(bcpl)/len(bcpl))
    print(statistics.stdev(bcpl))
    print()
    return sum(wcpl)/len(wcpl),statistics.stdev(wcpl),sum(bcpl)/len(bcpl),statistics.stdev(bcpl)

def processgame(inputpgnfile):
    
    global progress_bar
    global pbwindow

    engineinfo = []
    evals = []
    pgn = open(inputpgnfile)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    moveincri = 0
    i = 0
    for move in game.mainline_moves():
        moveincri += 1
    print('moveincri',moveincri)

    for move in game.mainline_moves():
        i += 1
        print()
        print(board) #THIS MEANS THAT THE FIRST EVAL IS THE STARTING POSITON

        eng.set_fen_position(board.fen())
        enginei = eng.get_top_moves(1)
        if len(enginei) > 0:
            print(enginei[0])
            engineinfo.append(enginei[0])

            if enginei[0]['Mate'] == None:
                    evals.append((False,enginei[0]['Centipawn']))
            else:
                    evals.append((True,enginei[0]['Mate']))
            board.push(move)

        event, values = pbwindow.read(timeout=10)
        if event == 'Cancel'  or event == sg.WIN_CLOSED:
            break
        progress_bar.UpdateBar(i + 1)

        print()
    print(len(evals))

    wacpl,wstd,bcpl,bstd = processevals(evals)
    print()
    pgn.close()
    pbwindow.close()
    return (engineinfo,wacpl,wstd,bcpl,bstd,len(evals))
    





pgn = open(pgnpath)
game = chess.pgn.read_game(pgn)
board = game.board()
moveincri = 0
for move in game.mainline_moves():
    moveincri += 1

    print('moveincri',moveincri)
    meterlayout = [[sg.Text('Processing Game...')],
          [sg.ProgressBar(moveincri, orientation='h', size=(20, 20), key='progressbar',bar_color=('green','white'))],
          [sg.Cancel()]]
    pbwindow = sg.Window('Loading', meterlayout)
    progress_bar = pbwindow['progressbar']

output = processgame(pgnpath)[1:]
pbwindow.close()
predictdata = {"WhiteACPL":[output[0]],"WstdACPL":[output[1]],"Moves":[output[4]],"BlackACPL":[output[2]],"BstdACPL":[output[3]]}
predictdf = pd.DataFrame(predictdata)
print()
res = model.predict(predictdf)
res = res.tolist()[0]
print(res)
print(type(res))
lastlayout = [
              [sg.Text('-WHITE-')],
              [sg.Text('  Predicted Rating:' + str(round(res[0])))],
              [sg.Text('  - ACPL: ' + str(round(output[0],1)))],
              [sg.Text('  - Std ACPL: ' + str(round(output[1],1)))],
              [sg.Text('-BLACK-')],
              [sg.Text('  Predicted Rating: ' + str(round(res[1])))],
              [sg.Text('  - ACPL: ' + str(round(output[2],1)))],
              [sg.Text('  - Std ACPL: ' + str(round(output[3],1)))],
              [sg.Text('Total Moves:' + str(output[4]-1))],
              
              [sg.Cancel()]
              ]
finalwindoow = sg.Window('Results', lastlayout)

while True:
    event,values = finalwindoow.read(timeout=10)
    time.sleep(0.1)
    if event == 'Cancel'  or event == sg.WIN_CLOSED:
            break
finalwindoow.close()
