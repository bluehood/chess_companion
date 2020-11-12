#!/usr/bin/env python3
import asyncio
import chess
import chess.svg
import chess.pgn
import chess.engine
import sys
import math
import lichess.api
from lichess.format import SINGLE_PGN

lichess_username = 'bluehood'
depth = 18

# Takes a chessboard configuration and returns Stockfish analysis of the position.
async def engine_analysis(board) -> None:
    #import engine 
    transport, engine = await chess.engine.popen_uci("./stockfish")

    #Perform analysis
    engine_info = await engine.analyse(board, chess.engine.Limit(depth=depth))

    await engine.quit()
    return(engine_info)

def import_game(pgn_file):
    try:
        pgn = open(pgn_file)
    except:
        print("[Error] Failed to load pgn file. Exiting.")
        exit()

    #Read game from the file
    try:
        first_game = chess.pgn.read_game(pgn)
    except:
        print("[Error] Invalid pgn format. Exiting.")
        exit()

    return(first_game)

def format_game(first_game):
    first_game_moves = str(first_game.mainline_moves())
    first_game_moves_list = []

    if str(first_game.headers).split(",")[4].split("=")[1].replace("\'", "") == lichess_username:
        report_side = "White"
    else:
        report_side = "Black"

    i = 1
    while True:
        lower_index = first_game_moves.find('{}.'.format(i))
        upper_index = first_game_moves.find('{}.'.format(i+1))

        if lower_index == -1:
            break

        if upper_index == -1:
            upper_index = len(first_game_moves)

        current_move = first_game_moves[lower_index:upper_index].replace('{}. '.format(i), '')
        current_move = current_move.strip()
        first_game_moves_list.append(current_move)
        i += 1

    return(first_game_moves_list, report_side)


def analysis_feedback(first_game, first_game_moves_list, white_to_move, report_side):
    #Setup board
    board = first_game.board()
    uci_list = []
    #Analyse opening postion. Save in uci_list
    asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
    engine_info = asyncio.run(engine_analysis(board))
    uci_list.append([str(engine_info["score"]),str(engine_info["pv"][0:2]).split('\'')[1::2]])
    mainline_moves = ['']

    #Analyse all moves in the game. Save in uci_list
    for move in first_game.mainline_moves():
        mainline_moves.append(str(str(move).split(' '))[2:-2])
        board.push(move)
        asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
        engine_info = asyncio.run(engine_analysis(board))
        #print(engine_info)

        #format centipawn score along with the two best moves given by the engine

        try:
            #print(board.turn, move)
            if board.turn == True:
                #Deal with mate pattern
                if str(str(engine_info["score"]).split('(')[1]) == "Mate":
                    current_score = str(str(engine_info["score"]).split('(')[2].split(')')[0])
                    current_score = str(current_score)[1:]
                    current_score = str(chess.engine.Mate(int(current_score)).score(mate_score=-10000000))
                    current_score = int(current_score) * -1
                    #print("1", current_score)
                else:
                    current_score = str(engine_info["score"])  
                    
                #print(current_score)
                uci_list.append([current_score, str(engine_info["pv"][0:2]).split('\'')[1::2]])
            
            # Convert relative score to absolute score
            elif board.turn == False:
                #Deal with mate pattern
                if str(str(engine_info["score"]).split('(')[1]) == "Mate":
                    current_score = str(str(engine_info["score"]).split('(')[2].split(')')[0])
                    current_score = str(current_score)[1:]
                    current_score = str(chess.engine.Mate(int(current_score)).score(mate_score=10000000))
                    #current_score = int(current_score) + 2*int(str(current_score[-2:]))
                    #print("2", current_score)
                else:

                    current_score = (str(engine_info["score"]))
                
                uci_list.append([current_score, str(engine_info["pv"][0:2]).split('\'')[1::2]])
                
        except:

            if board.turn == True:
                #Deal with mate pattern
                #print(str(engine_info["score"]).split('(')[1])
                if str(str(engine_info["score"]).split('(')[1]) == "Mate":
                    current_score = str(str(engine_info["score"]).split('(')[2].split(')')[0])
                    current_score = str(current_score)[1:]
                    current_score = str(chess.engine.Mate(int(current_score)).score(mate_score=-10000000))
                    current_score = int(current_score) * -1
                    #print("3", current_score)
                else:
                    current_score = str(engine_info["score"])

                uci_list.append([current_score, 0])   
            
            elif board.turn == False:
                #Deal with mate pattern
                #print(str(engine_info["score"]).split('(')[1])
                if str(str(engine_info["score"]).split('(')[1]) == "Mate":
                    current_score = str(str(engine_info["score"]).split('(')[2].split(')')[0])
                    current_score = str(current_score)[1:]
                    current_score = str(chess.engine.Mate(int(current_score)).score(mate_score=10000000))
                    #current_score = int(current_score) + 2*int(str(current_score[-2:]))
                    #print("4", current_score)
                    #uci_list.append([current_score, 0])
                    
                else:
                    current_score = str(engine_info["score"])


                uci_list.append([current_score, 0])   
                

    for x in range(0, len(uci_list)):
        #print(uci_list[x][0], type(uci_list[x][0]))
        if isinstance(uci_list[x][0], str) == True:
            if "BLACK" in uci_list[x][0]  and "-" in uci_list[x][0]:
                uci_list[x][0] = uci_list[x][0].replace("-", "+")
            elif "BLACK" in uci_list[x][0]  and "+" in uci_list[x][0]:
                uci_list[x][0] = uci_list[x][0].replace("+", "-")
  
    #Calculate move clasification e.g. best move, blunder, ...

    move_clasification_count = [["Best Move",0, 0],["Excellent",0, 0],["Good",0, 0],["Okay",0, 0],["Inaccuracy",0, 0],["Mistake",0, 0],["Blunder",0, 0]]

    #for x in uci_list:
     #  print(x)

    for x in range(0, len(uci_list)):
        if x == 0:
            previous_uci = 0.30
        else:
            previous_uci = current_uci

        try:
            current_uci = uci_list[x][0].split("(")[2].split(")")[0]
        except:
            current_uci = int(uci_list[x][0])

        difference_uci = int(current_uci) - int(previous_uci)

        #Differentiate between white and black moves. 
        if (x % 2) == 0:
            difference_uci = -1 * difference_uci
        #Calculate whether the move was the best move
        if uci_list[x][1] != 0:
            if mainline_moves[x] in uci_list[x][1]:
                uci_list[x].append("Best Move")
                move_clasification_count[0][1] += 1
                continue
        #Calculate move score based on uci
        if difference_uci >= 40:
            uci_list[x].append("Excellent")
            if (x % 2) == 0:
                move_clasification_count[1][2] += 1
            else:
                move_clasification_count[1][1] += 1
        elif 0 <= difference_uci < 40:
            uci_list[x].append("Good")
            if (x % 2) == 0:
                move_clasification_count[2][2] += 1
            else:
                move_clasification_count[2][1] += 1
        elif -40 <= difference_uci < 0:
            uci_list[x].append("Okay")
            if (x % 2) == 0:
                move_clasification_count[3][2] += 1
            else:
                move_clasification_count[3][1] += 1
        elif -90 <= difference_uci < -40:
            uci_list[x].append("Inaccuracy")
            if (x % 2) == 0:
                move_clasification_count[4][2] += 1
            else:
                move_clasification_count[4][1] += 1
        elif -200 <= difference_uci < -90:
            uci_list[x].append("Mistake")
            if (x % 2) == 0:
                move_clasification_count[5][2] += 1
            else:
                move_clasification_count[5][1] += 1
        elif difference_uci < -200:
            uci_list[x].append("Blunder")
            if (x % 2) == 0:
                move_clasification_count[6][2] += 1
            else:
                move_clasification_count[6][1] += 1


    report_moves = []

    # print out results of analysis
    for x in range(1, len(uci_list)):
        #if x == 0:
        #    continue
        if (x % 2) != 0:
            buf = " " * (15 - len("{}. {}".format(math.ceil(x/2),first_game_moves_list[math.floor(x/2)].split(' ')[0])))
           
            try:
                 output_string = "{}. {}{}{}".format(math.ceil(x/2),first_game_moves_list[math.floor(x/2)].split(' ')[0], buf, float(uci_list[x][0].split("(")[2].split(")")[0])/100)
            except:
                 output_string = "{}. {}{}{}".format(math.ceil(x/2),first_game_moves_list[math.floor(x/2)].split(' ')[0], buf, float(uci_list[x][0])/100)
            

            buf2 = " " * (25 - len(output_string))
            try:
                output_string += buf2 + str(uci_list[x][2])
            except: 
                output_string += buf2 + "   Mate to follow"
            buf3 = " " * (40 - len(output_string))
            try:
                output_string += buf3 + "Best Move was {}".format(str(uci_list[x - 1][1][0]))
                if report_side == "White":
                    if "Blunder" in output_string or "Mistake" in output_string or "Inaccuracy" in output_string:
                        report_moves.append(output_string)

            except:
                output_string += buf3 + "Game Over!"
            print(output_string)
        else:
            buf = " " * (15 - len("{}. .. {}".format(math.ceil(x/2),first_game_moves_list[math.ceil(x/2) - 1].split(' ')[1])))
    
            try:
                output_string = "{}. .. {}{}{}".format(math.ceil(x/2),first_game_moves_list[math.ceil(x/2) - 1].split(' ')[1], buf, float(uci_list[x][0].split("(")[2].split(")")[0])/100, uci_list[x][1])
            except:
                output_string = "{}. .. {}{}{}".format(math.ceil(x/2),first_game_moves_list[math.ceil(x/2) - 1].split(' ')[1], buf, float(uci_list[x][0])/100, uci_list[x][1])
            
            buf2 = " " * (25 - len(output_string))
            try:
                output_string += buf2 + str(uci_list[x][2])
            except: 
                output_string += buf2 + "   Mate to follow"            
            buf3 = " " * (40 - len(output_string))
            try:
                output_string += buf3 + "Best Move was {}".format(str(uci_list[x - 1][1][0]))
                if report_side == "Black":
                    if "Blunder" in output_string or "Mistake" in output_string or "Inaccuracy" in output_string:
                        report_moves.append(output_string)
            except:
                output_string += buf3 + "Game Over!"
            print(output_string)
    
    print("\nMoves to Improve")
    for x in report_moves:
        print(x)
    ##Needs work - Seperate for white and black
    #print(move_clasification_count)
    print("\n")
    print(" " * 19, "White", " " * 12, "Black")

    for x in range(0, len(move_clasification_count)):
        buf1 = " " * (20 - len(move_clasification_count[x][0]))
        buf2 = " " * (40 - len(move_clasification_count[x][0]) - len(buf1) - len(str(move_clasification_count[x][1])))

        print("{}{}{}{}{}".format(move_clasification_count[x][0], buf1, move_clasification_count[x][1], buf2, move_clasification_count[x][2]))
                
         
    return(0)

# The main function of the application 
def main():
    #Import pgn from Lichess
    if len(sys.argv) != 2:
        pgn = lichess.api.user_games(lichess_username, max=1, format=SINGLE_PGN)
        with open('lastest_game.pgn', 'w') as f:
            f.write(pgn)

        game_file = 'lastest_game.pgn'
    else:
        game_file = sys.argv[1]
        

    #Import pgn game file
    first_game = import_game(game_file)

    #Format Game moves
    first_game_moves_list, report = format_game(first_game)
    
    #Play through the position and analyse the moves using the Stockfish engine
    analysis_feedback(first_game, first_game_moves_list, True, report)
    return(0)
    
        
if __name__ == '__main__':
    
    main()
    exit()
