# chess_companion
A simple program that will analyse and report on chess games, either supplied as PGN files or your latest game off lichess.com. The program uses Stockfish for this analysis which should be downloaded from https://stockfishchess.org/download/. 

The project is built in Python 3.9 - other version will likely not work. The project is developed in Linux but will likely work on other platforms. 

Installation: 
Clone this repository to you machine
'''
git clone https://github.com/bluehood/chess_companion.git
'''
You should then insall the requirements
'''
pip3 install -r requirements.txt
'''
If you decide to use the lichess.com feature you must code your username into main.py. This a variable on line 12. You can also specify the depth of analysis on line 13. 

Ensure the stockfish engine executable is in the same directory as your download. 

# Usage
To analyse a game from a local pgn run
'''
python3 main.py ./path/to/file
'''
To analyse your most recent game from lichess.com run
'''
python3 main.py 
'''
# Example Output:
'''
bluehood@ubuntu:~/Documents/programming/python/chess_analysis$ python3 main.py 
1. e4          0.15      Good           Best Move was e2e4
1. .. c5       0.28      Okay           Best Move was c7c5
2. Nf3         0.1       Okay           Best Move was g1f3
2. .. d6       0.39      Okay           Best Move was d7d6
3. d4          0.57      Good           Best Move was d2d4
3. .. cxd4     0.57      Good           Best Move was c5d4
4. Nxd4        0.38      Okay           Best Move was f3d4
4. .. Nf6      0.46      Okay           Best Move was g8f6

...

46. gxf3       -6.56     Okay           Best Move was g2f3
46. .. exf3    -5.76     Inaccuracy     Best Move was e4f3
47. Re1+       -6.44     Inaccuracy     Best Move was g4h6
47. .. Kf5     -6.32     Okay           Best Move was d6e4
48. Nxh6+      -7.17     Inaccuracy     Best Move was g4e3
48. .. Kf4     -8.4      Excellent      Best Move was f5f4
49. Re6        -99999.98  Excellent      Best Move was e1c1
49. .. Ra1+    -99999.99 Excellent      Best Move was a2a1

Moves to Improve
6. .. Nbxd7    0.28      Inaccuracy     Best Move was d8d7
8. .. Be7      0.57      Mistake        Best Move was f6e4
13. .. Ne5     -0.47     Blunder        Best Move was d8b6
17. .. Bb4     -4.7      Blunder        Best Move was b2c3
18. .. Qxc3    -4.38     Inaccuracy     Best Move was b2c3
19. .. Qxd2    -4.17     Inaccuracy     Best Move was c3d2
21. .. Re8     -4.09     Inaccuracy     Best Move was c2c5
24. .. Rf8     -3.32     Mistake        Best Move was g8f8
28. .. Ke7     -5.53     Mistake        Best Move was f6f5
31. .. Kd5     -6.07     Inaccuracy     Best Move was e6e7
38. .. Kd7     -7.01     Inaccuracy     Best Move was e6d7
39. .. g5      -6.88     Inaccuracy     Best Move was a6a5
42. .. Kd7     -8.78     Inaccuracy     Best Move was e6f5
43. .. g4      -7.59     Mistake        Best Move was a6a5
44. .. Ke6     -7.77     Inaccuracy     Best Move was d7e6
45. .. f3      -6.32     Blunder        Best Move was h6h5
46. .. exf3    -5.76     Inaccuracy     Best Move was e4f3


                    White              Black
Best Move           0                   0
Excellent           2                   2
Good                7                   12
Okay                18                  18
Inaccuracy          13                  10
Mistake             7                   4
Blunder             2                   3
'''

Current Issues:
+ The Best Move function is not working. Even if you made the best move it will not be output by the program. This is due to a difference in notation between the Stockfish engine output and algebriac notation. Working to fix this. 
