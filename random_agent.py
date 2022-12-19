import random
import gomoku
import copy
import math
from gomoku import Board, Move, GameState, valid_moves, check_win

class tree_node():
    def __init__(self, state, parentNode = None, last_move = None):
        self.state = state
        self.parent=parentNode
        self.children=[]
        self.last_move = last_move
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

    def find_unexplored_move(self, moves: list, children: list):
        if moves == []:
            return None
        for i in moves:
            if i in children:
                moves.remove(i)
            else:
                return i

    def expand(self, node: tree_node) -> tree_node:
        if check_win(node.state[0], node.last_move) or len(valid_moves(node.state)) == 0: # if n is terminal (game finished)
            return node

        v_moves = copy.deepcopy(valid_moves(node.state))
        random.shuffle(v_moves)
        if len(node.children) != len(v_moves): # node is fully expanded if its number of children is equal to the number of valid moves in that game state - ALDS Reader
            copy_state = copy.deepcopy(node.state)
            new_move = self.find_unexplored_move(v_moves, node.children)
            is_valid, is_new, new_state = gomoku.move(copy_state, new_move)
            new_child_node = tree_node(new_state, node, new_move)
            node.children.append(new_child_node) # a random not-yet-explored move is selected to add as a child node
            return new_child_node

        return self.expand(node.highest_uct())

    def rollout(self, node: tree_node, g_state: GameState) -> float:
        if gomoku.check_win(g_state[0], node.last_move):
            if node.state[1] % 2 != self.black:
                return 1
            if node.state[1] % 2 == self.black:
                return -1
            else:
                return 0
        moves = copy.deepcopy(valid_moves(g_state))
        random.shuffle(moves)
        while len(moves) > 0: # cant pop() when len(moves) = 0
            random_move = moves.pop()
            is_valid, is_win, g_state = gomoku.move(g_state, random_move) # random move in state S

        if gomoku.check_win(g_state[0], node.last_move):
            if node.state[1] % 2 != self.black:
                return 1
            if node.state[1] % 2 == self.black:
                return -1
        else: #draw
            return 0

    def backup(self, value: float, node: tree_node) -> None:
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

        root = tree_node(copy.deepcopy(state), None, last_move)
        while max_time_to_move > 0:
            leaf = self.expand(root)
            for i in range(8):
                val = self.rollout(leaf, copy.deepcopy(state))
                self.backup(val, leaf)
            max_time_to_move -=1

        return root.bestest_move()

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "1686836_David_de_Jong"
