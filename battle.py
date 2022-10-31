"""Assignment 3 - CSP battleship"""
import math
import sys
from heapq import heappush, heappop
from dataclasses import dataclass, field
from typing import Any

import numpy as np


class State:
    """
    This class record a state of board in dictionary.

    Attributes:
    map: A dictionary stores the position of each space (treat it as coordinates) as key and
    the corresponding value of each key is a list.
    In the list, we store the type of piece as string ('0' represents empty space;
    'S' represent submarine; 'W' represents water; 'L' represents left end of horizontal ship;
    'R' represents right end of horizontal ship; 'T' represents the top end of vertical ship;
    'B' represents the bottom end of vertical ship; 'M' represents a middle segment of a ship).

    ship_domain: A dictionary stores the domain of left end or top end of ship
    (or a certain position of submarine).

    ship_remain: A dictionary stores the number of ships we need to place on the board for winning
    the game.

    Method:
    - place(position: tuple, ship: str):
        Place a ship (variable 'ship' represents the type of ship) on the position
        where is the left end or top end of a ship placed on (or a certain position for submarine).
    - display():
        print the state information (where is each piece at) as "matrix-like" form to console.

    """
    map: dict[tuple, str]
    ship_domain: dict[str, list[tuple]]
    ship_remain: dict[str, int]
    row_con: list[int]
    col_con: list[int]

    def __init__(self) -> None:
        self.map = dict()
        self.ship_domain = {'submarines': [], 'destroyers': [], 'cruisers': [], 'battleships': []}
        self.ship_remain = {'submarines': 0, 'destroyers': 0, 'cruisers': 0, 'battleships': 0}
        self.row_con = []
        self.col_con = []

    def __str__(self):
        """print the state information (where is each piece at) as
        "matrix-like" form to console."""
        shape = int(math.sqrt(len(self.map)))
        lst = []
        result = ''
        for _ in range(shape):
            lst.append(['0'] * shape)

        for key in self.map:
            lst[key[1]][key[0]] = self.map[key]

        for i in range(shape):
            result += ''.join(lst[i])
            result += '\n'
        return result

    def __eq__(self, other):
        """
        Return True if all items in other's red and black are same as self's
        """
        # Check whether they have same number of elements in map
        if len(self.map) != len(other.map):
            return False

        # Check all key and the corresponding value of that key are
        # same in self's and other's map
        for key in self.map:
            if key not in other.map:
                return False
            elif self.map[key] != other.map[key]:
                return False
        return True

    def place(self, position: tuple, ship: str, direction: str = None) -> None:
        """Place a ship (variable 'ship' represents the type of ship) on the position where is the
        left end (direction = 'h') or top end (direction = 'v') of
        a ship placed on (or a certain position for submarine)."""
        if ship != 'submarines' and direction is None:
            print('ERROR: argument \'direction\' is missing')
            return
        x = position[0]
        y = position[1]
        shape = int(math.sqrt(len(self.map)))
        check_lst = []
        check_lst2 = []
        if ship == 'submarines':
            # Check the surrounding of position is empty or not
            check_lst = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                         (x - 1, y), (x + 1, y),
                         (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]
            check_lst = [tup for tup in check_lst if 0 <= tup[0] < shape and 0 <= tup[1] < shape]

            for pos in check_lst:
                if self.map[pos] != '0' and self.map[pos] != 'W':
                    return

            # Check whether the spaces of placing a ship is occupied,
            # and place it if there are all empty
            if self.map[position] != '0':
                return
            else:
                self.map[position] = 'S'
                self.ship_remain['submarines'] -= 1

        elif ship == 'destroyers':
            # Check the surrounding of position is empty or not
            if direction == 'v':
                check_lst = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                             (x - 1, y), (x + 1, y),
                             (x - 1, y + 1), (x + 1, y + 1),
                             (x - 1, y + 2), (x, y + 2), (x + 1, y + 2)]
                check_lst2 = [(x, y), (x, y + 1)]
            else:
                check_lst = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x + 2, y - 1),
                             (x - 1, y), (x + 2, y),
                             (x - 1, y + 1), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1)]
                check_lst2 = [(x, y), (x + 1, y)]
            check_lst = [tup for tup in check_lst if 0 <= tup[0] < shape and 0 <= tup[1] < shape]
            check_lst2 = [tup for tup in check_lst2 if 0 <= tup[0] < shape and 0 <= tup[1] < shape]

            for pos in check_lst:
                if self.map[pos] != '0' and self.map[pos] != 'W':
                    return
            # Check whether the spaces of placing a ship is valid or unoccupied,
            # and place it if there are all empty
            if len(check_lst2) != 2:
                return
            for pos in check_lst2:
                if self.map[pos] != '0':
                    return
            # Place ship
            if direction == 'h':
                self.map[check_lst2[0]] = 'L'
                self.map[check_lst2[1]] = 'R'
                self.ship_remain['destroyers'] -= 1
            else:
                self.map[check_lst2[0]] = 'T'
                self.map[check_lst2[1]] = 'B'
                self.ship_remain['destroyers'] -= 1

        elif ship == 'cruisers':
            # Check the surrounding of position is empty or not
            if direction == 'h':
                check_lst = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x + 2, y - 1),
                             (x + 3, y - 1),
                             (x - 1, y), (x + 3, y),
                             (x - 1, y + 1), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1),
                             (x + 3, y + 1)]
                check_lst2 = [(x, y), (x + 1, y), (x + 2, y)]
            else:
                check_lst = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                             (x - 1, y), (x + 1, y),
                             (x - 1, y + 1), (x + 1, y + 1),
                             (x - 1, y + 2), (x + 1, y + 2),
                             (x - 1, y + 3), (x, y + 3), (x + 1, y + 3)]
                check_lst2 = [(x, y), (x, y + 1), (x, y + 2)]
            check_lst = [tup for tup in check_lst if 0 <= tup[0] < shape and 0 <= tup[1] < shape]
            check_lst2 = [tup for tup in check_lst2 if 0 <= tup[0] < shape and 0 <= tup[1] < shape]

            for pos in check_lst:
                if self.map[pos] != '0' and self.map[pos] != 'W':
                    return
            # Check whether the spaces of placing a ship is valid or unoccupied,
            # and place it if there are all empty
            if len(check_lst2) != 3:
                return
            for pos in check_lst2:
                if self.map[pos] != '0':
                    return
            # Place ship
            if direction == 'h':
                self.map[check_lst2[0]] = 'L'
                self.map[check_lst2[1]] = 'M'
                self.map[check_lst2[2]] = 'R'
                self.ship_remain['cruisers'] -= 1
            else:
                self.map[check_lst2[0]] = 'T'
                self.map[check_lst2[1]] = 'M'
                self.map[check_lst2[2]] = 'B'
                self.ship_remain['cruisers'] -= 1

        elif ship == 'battleships':
            # Check the surrounding of position is empty or not
            if direction == 'h':
                check_lst = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x + 2, y - 1), (x + 3, y - 1), (x + 4, y + 1),
                             (x - 1, y), (x + 4, y),
                             (x - 1, y + 1), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1), (x + 3, y + 1), (x + 4, y + 1)]
                check_lst2 = [(x, y), (x + 1, y), (x + 2, y), (x + 3, y)]
            else:
                check_lst = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                             (x - 1, y), (x + 1, y),
                             (x - 1, y + 1), (x + 1, y + 1),
                             (x - 1, y + 2), (x + 1, y + 2),
                             (x - 1, y + 3), (x + 1, y + 3),
                             (x - 1, y + 4), (x, y + 4), (x + 1, y + 4)]
                check_lst2 = [(x, y), (x, y + 1), (x, y + 2), (x, y + 3)]
            check_lst = [tup for tup in check_lst if 0 <= tup[0] < shape and 0 <= tup[1] < shape]
            check_lst2 = [tup for tup in check_lst2 if 0 <= tup[0] < shape and 0 <= tup[1] < shape]

            for pos in check_lst:
                if self.map[pos] != '0' and self.map[pos] != 'W':
                    return
            # Check whether the spaces of placing a ship is valid or unoccupied,
            # and place it if there are all empty
            if len(check_lst2) != 4:
                return
            for pos in check_lst2:
                if self.map[pos] != '0':
                    return
            # Place ship
            if direction == 'h':
                self.map[check_lst2[0]] = 'L'
                self.map[check_lst2[1]] = 'M'
                self.map[check_lst2[2]] = 'M'
                self.map[check_lst2[3]] = 'R'
                self.ship_remain['battleships'] -= 1
            else:
                self.map[check_lst2[0]] = 'T'
                self.map[check_lst2[1]] = 'M'
                self.map[check_lst2[2]] = 'M'
                self.map[check_lst2[3]] = 'B'
                self.ship_remain['battleships'] -= 1
        else:
            return


def txt_to_state(file: str) -> State:
    """Return a State that convert input form to a game board state."""
    f = open(file, 'r')
    str_lst = f.readlines()
    result = State()
    shape = len(str_lst[0]) - 1  # Not include '\n'
    for i in str_lst[0]:
        if i != '\n':
            result.row_con.append(int(i))
    for i in str_lst[1]:
        if i != '\n':
            result.col_con.append(int(i))
    for i in range(len(str_lst[2]) - 1):
        if i == 0:
            result.ship_remain['submarines'] = int(str_lst[2][i])
        elif i == 1:
            result.ship_remain['destroyers'] = int(str_lst[2][i])
        elif i == 2:
            result.ship_remain['cruisers'] = int(str_lst[2][i])
        else:
            result.ship_remain['battleships'] = int(str_lst[2][i])

    for y in range(shape):
        for x in range(shape):
            result.map[(x, y)] = str_lst[y + 3][x]
    f.close()
    return result
