import os 
import chess.pgn
import chess
import pandas as pd 
from stockfish import Stockfish
import time
import statistics
import re
import FreeSimpleGUI as sg

pgnspath = "PUTPATHHERE" #REPLACE THIS PATH WITH THE PATH TO YOUR FOLDER WITH PGNS
afterpath = "PUTPATHHERE" #REPLACE THIS PATH WITH PROCESSED GANES FOLDER. ALL PROCESSED GAMES WILL BE MOVED TO THIS PATH.


csvpath = "PUTPATHHERE" # REPLACE THIS PATH WITH PATH TO THE CSV FILE
stockfishpath = "PUTPATHHERE" #STOCKFISH PATH WILL ALSO NEED TO BE DEFINED

eng = Stockfish(path=stockfishpath)
eng.set_depth(18) 
eng.set_turn_perspective(False)

timed = time.time()



def geteval(fen):
    eng.set_fen_position(fen)
    return eng.get_top_moves(1)

print(time.time()-timed)
def rff(fpath):
    with open(fpath) as f:
        return f.read()
        

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

        if (evalslist[plylook][0] == False) and (evalslist[plylook+1][0] == False):
            n = max(evalslist[plylook+1][1]-evalslist[plylook][1],0)
            bcpl.append(n)
        elif (evalslist[plylook][0] == True) and (evalslist[plylook+1][0] == False):
             bcpl.append(max(1000+(max(evalslist[plylook+1][1],-900)),1200))
        else:
            try:
             if evalslist[plylook][1]/abs(evalslist[plylook][1]) == evalslist[plylook+1][1]/abs(evalslist[plylook+1][1]):
                 pass
             else:
                bcpl.append(1400) #Two points extra if you went from +M1 to -M1
            except ZeroDivisionError:
                pass
         #   print(n)
        plylook += 2
    print(sum(bcpl)/len(bcpl))
    print(statistics.stdev(bcpl))
    print()
    return sum(wcpl)/len(wcpl),statistics.stdev(wcpl),sum(bcpl)/len(bcpl),statistics.stdev(bcpl)

def processgame(inputpgnfile):
    engineinfo = []
    evals = []
    pgn = open(inputpgnfile)
    game = chess.pgn.read_game(pgn)
    board = game.board()
    for move in game.mainline_moves():
        
        print()
        print(board) #THIS MEANS THAT THE FIRST EVAL IS THE STARTING POSITON
  
        enginei = geteval(board.fen())
        if len(enginei) > 0:
            print(enginei[0])
            engineinfo.append(enginei[0])
            '''
            #Okay so I decided to comment out this old version where I returned a capped  evaluation at +- 1300 centipawns for non-mates and 1300-1440 for mates.
            # A new calculate  will be just added to the acpl list interpreter function (processevals())  and explained
            
            if enginei[0]['Mate'] == None:
                if abs(enginei[0]['Centipawn']) <1300:  
                    evals.append(enginei[0]['Centipawn'])
                else:
                    evals.append((enginei[0]['Mate']/abs(enginei[0]['Mate']))*1300)
            else:
                if enginei[0]['Mate'] <7:
                    evals.append((1460 - abs(20*enginei[0]['Mate'])) *(enginei[0]['Mate']/abs(enginei[0]['Mate'])))
                else:
                    evals.append(1400*(enginei[0]['Mate']/abs(enginei[0]['Mate'])))
            '''
            if enginei[0]['Mate'] == None:
                    evals.append((False,enginei[0]['Centipawn']))
            else:
                    evals.append((True,enginei[0]['Mate']))
            board.push(move)
        print()
    print(len(evals))
    if len(evals) < 5: #SKIPS GAMES 4 MOVES OR LESS
        pgn.close()
        os.rename(inputpgnfile,os.path.join(afterpath,os.path.basename(inputpgnfile)))
    else:
        wacpl,wstd,bcpl,bstd = processevals(evals)
        print()
        addtodata([rff(inputpgnfile)],engineinfo,wacpl,wstd,bcpl,bstd,len(evals),game.headers["WhiteElo"],game.headers["BlackElo"])
    print()
    pgn.close()
    os.rename(inputpgnfile,os.path.join(afterpath,os.path.basename(inputpgnfile)))



def addtodata(pgn,evals,wacpl,wstd,bcpl,bstd,numevals,welo,belo):
    df = pd.DataFrame ( {"PGN":pgn,"Evals":[evals],"wacpl":wacpl,"wstd":wstd,"bacpl":bcpl,"bstd":bstd,"Nevals":numevals,"Welo":welo,"Belo":belo} ) 
    df.to_csv(csvpath,mode='a',index=False,header=False,sep="|")

for file in os.listdir(pgnspath):
    processgame(os.path.join(pgnspath,file))
