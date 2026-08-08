# ChessEloGuesser
A Easy-to-use implementation of machine learning to predict the ratings of two similarly-rated players based on stats extracted from a single game.

<h2>Project Screenshots:</h2>

<h2> Starting Menu:</h2>

<img src="https://github.com/PixelsStuff/ChessEloGuesser/blob/main/MenuIMG.png">

<h2> Results Page:</h2>


<img src="https://github.com/PixelsStuff/ChessEloGuesser/blob/main/ResultIMG.png">



<h2> Installation:</h2>


<p>1. Ensure you have the latest version of Python installed</p>

<p>2. Install the Requirements</p>

```
pip install -r requirements.txt
```
<p>3. Make sure you have "GamesData.csv" in the same directory as the program file, "App.py"
<p>4. you can run "App.py" in python

<h2>Usage</h2>h2>

For Estimating Ratings: Run the program and input the paths to your engine and PGN. The next time the program is run those paths will be saved. You can only input games that last more than 3 moves.

For adding more games to the dataset: You need to create a folder to store the PGNS you want to process. Then modify each necessary path of "pgnphraser.py" before running it. Pgns from that file will move to the processed pgn file and update GamesData.csv with the appropritate infromation. 



