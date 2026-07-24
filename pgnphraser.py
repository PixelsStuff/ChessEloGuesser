import os 
import chess.pgn
import chess
import pandas as pd 
from stockfish import Stockfish
import time
import statistics
import re
import FreeSimpleGUI as sg

#https://pypi.org/project/stockfish/
#https://python-chess.readthedocs.io/en/latest/

pgnspath = r"C:\Users\coolg\OneDrive\Desktop\Tools\RatingEstimator\Games"
afterpath = r"C:\Users\coolg\OneDrive\Desktop\Tools\RatingEstimator\ProcessedGames" #ALL PROCESSED GAMES WILL BE MOVED TO THIS PATH


csvpath = r"C:\Users\coolg\OneDrive\Desktop\Tools\RatingEstimator\GamesData.csv"
stockfishpath = r"C:\Users\coolg\Downloads\SF18\stockfish\stockfish-windows-x86-64-avx2.exe"

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
    if len(evals) < 5: #SKIPS GAMES ONE MOVE OR LESS
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

#tstprocess = [(False, 48), (False, 28), (False, 30), (False, 35), (False, 59), (False, 56), (False, 54), (False, 60), (False, 56), (False, 55), (False, 52), (False, 43), (False, 48), (False, 31), (False, 90), (False, 33), (False, 80), (False, 73), (False, 90), (False, 57), (False, 107), (False, -19), (False, 82), (False, 15), (False, 14), (False, 13), (False, 127), (False, 86), (False, 169), (False, 151), (False, 155), (False, 166), (False, 195), (False, 176), (False, 281), (False, 257), (False, 267), (False, 250), (False, 279), (False, 280), (False, 283), (False, 263), (False, 261), (False, 93), (False, 110), (False, 36), (False, 14), (False, -169), (False, -173), (False, -153), (False, -125), (False, -190), (False, -123), (False, -201), (False, -214), (False, -219), (False, -199), (False, -226), (False, -170), (False, -248), (False, -249), (False, -240), (False, -210), (False, -253), (False, -258), (False, -248), (False, -255), (False, -257), (False, -228), (False, -340), (False, -270), (False, -260), (False, -250), (False, -257), (False, -264), (False, -287), (False, -218), (False, -255), (False, -217), (False, -218), (False, -211), (False, -414), (False, -42), (False, -338), (False, -377), (False, -460), (False, -476), (False, -484), (False, -475), (False, -482), (False, -484), (False, -477), (False, -472), (False, -466), (False, -475), (False, -490), (False, -369), (False, -427), (False, -74), (False, -98), (False, -94), (False, -53), (False, -41), (False, -167), (False, -149), (False, -202), (False, -215), (False, -249), (False, -260), (False, -337), (False, -387), (False, -416), (False, -333), (False, -388), (False, -309), (False, -404), (False, -440), (False, -450), (False, -491), (False, -491), (False, -273), (False, -235), (False, -236), (False, -617), (False, -684), (False, -727), (False, -720), (False, -740), (False, -770), (False, -762), (False, -804), (False, -813), (False, -873), (False, -970), (False, -994), (True, -8), (True, -7), (True, -2), (True, -1), (True, -1)]
#print(processevals(tstprocess))



#df = pd.DataFrame ( {"ACPL":[80,30],"Rating":[800,2300]} ) 

#df.to_csv(csvpath,mode='a',index=False,header=False)