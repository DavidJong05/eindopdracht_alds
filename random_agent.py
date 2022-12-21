import random
import gomoku
import copy
import math
import time
from gomoku import Board, Move, GameState, valid_moves, check_win

class tree_node():
    def __init__(self, state, parentNode = None, last_move = None, v_moves = None):
        self.state = state
        self.parent=parentNode
        self.children=[]
        self.last_move = last_move
        self.v_moves = v_moves
        self.Q = 0
        self.N = 0

    def uct(self):
        value = self.Q/self.N
        c = math.sqrt(2)
        parents_visited = math.sqrt((math.log(self.parent.N)) / self.N)
        result = value + c * parents_visited
        return result

    def highest_uct(self):
        val = -math.inf
        highest = None
        for ch in self.children:
            if ch.uct() > val:
                val = ch.uct()
                highest = ch
        return highest

    def bestest_move(self):
        val = -math.inf
        bestest = None
        for ch in self.children:
            ch_val = ch.Q/ch.N
            if ch_val > val:
                val = ch_val
                bestest = ch.last_move
        return bestest

class random_dummy_player:
    """This class specifies a player that just does random moves.
    The use of this class is two-fold: 1) You can use it as a base random roll-out policy.
    2) it specifies the required methods that will be used by the competition to run
    your player
    """

    def __init__(self, black_: bool = True):
        """Constructor for the player."""
        self.black = black_

    def new_game(self, black_: bool):
        """At the start of each new game you will be notified by the competition.
        this method has a boolean parameter that informs your agent whether you
        will play black or white.
        """
        self.black = black_

    def result_of_game(self, ply, player):
        if player: # black = 1 = true
            if ply % 2 == 0:
                return 1
            elif ply % 2 == 1:
                return -1
            else:
                return 0
        if player == False: # white = 2 = false
            if ply % 2 == 1:
                return 1
            elif ply % 2 == 0:
                return -1
            else:
                return 0

    def expand(self, node: tree_node) -> tree_node:
        if check_win(node.state[0], node.last_move) or len(node.v_moves) == 0:
            return node

        valid_move_list = copy.deepcopy(node.v_moves)
        copy_state = copy.deepcopy(node.state)

        if len(node.children) != len(valid_move_list):
            new_move = random.choice(valid_move_list)
            is_valid, is_new, new_state = gomoku.move(copy_state, new_move)
            valid_move_list.remove(new_move)
            new_child_node = tree_node(new_state, node, new_move, valid_move_list)
            node.children.append(new_child_node)
            return new_child_node

        return self.expand(node.highest_uct())

    def rollout(self, node) -> float:
        if check_win(node.state[0], node.last_move) or len(node.v_moves) == 0:
            return self.result_of_game(node.state[1], self.black)
        moves = copy.deepcopy(node.v_moves)
        random.shuffle(moves)
        new_state = copy.deepcopy(node.state)
        while len(moves) > 0:  # cant pop() when len(moves) = 0
            random_move = moves.pop()
            is_valid, is_win, new_state = gomoku.move(new_state, random_move)  # random move in state S

        if check_win(new_state[0], node.last_move):
            return self.result_of_game(new_state[1], self.black)
        elif len(moves) == 0:
            return 0

    def backup(self, value: float, node) -> None:
        while node is not None:
            node.N += 1
            node.Q += value
            node = node.parent

    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move:
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """
        startTime = time.time_ns()
        v_moves = copy.deepcopy(valid_moves(state))
        root = tree_node(copy.deepcopy(state), None, last_move, v_moves)
        counter = 0
        while (((time.time_ns() - startTime) / 1000000) < max_time_to_move):
            counter+=1
            child = self.expand(root)
            for i in range(8):
                val = self.rollout(child)
                self.backup(val, child)
        print(f"{str(counter)} amount of loops")
        return root.bestest_move()

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "1686836_David_de_Jong"
