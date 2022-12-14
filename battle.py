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

    ship_domain: A dictionary stores a dictionary of domain of left end or top end of a ship with
    type of ship as key; and in
     - Example:
       - ship_domain = {'submarines': {0: [(0, 0), (0, 1), ...]},
                        'cruisers': {0: {(0, 0): ['h', 'v'], (0, 1): ['h', 'v'], ...}}}.

    ship_remain: A dictionary stores the number of ships we need to place on the board for winning
    the game.

    ship_seg: A dictionary stores the position of each ship segments (not complete ship) as key
    and the cooresponding value is what type of segment it is.

    Method:
    - place(position: tuple, ship: str):
        Place a ship (variable 'ship' represents the type of ship) on the position
        where is the left end or top end of a ship placed on (or a certain position for submarine).
    - c_surrounding(ship: str, ship_ind1                                      : int, ship2, ship2_ind: int):
        Return True if ship and ship2 are both in safe distance (Include checking the row
        and column constrain).

    """
    map: dict[tuple, str]
    ship_domain: dict[str, dict]
    ship_remain: dict[str, int]
    ship_seg: dict[tuple, str]
    row_con: list[int]
    col_con: list[int]

    def __init__(self) -> None:
        self.map = dict()
        self.ship_domain = {'submarines': dict(), 'destroyers': dict(), 'cruisers': dict(),
                            'battleships': dict()}
        self.ship_remain = {'submarines': 0, 'destroyers': 0, 'cruisers': 0, 'battleships': 0}
        self.ship_seg = dict()
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
        if self.map != other.map or \
                self.ship_domain != other.ship_domain or \
                self.ship_remain != other.ship_remain or \
                self.ship_seg != other.ship_seg or \
                self.row_con != other.row_con or \
                self.col_con != other.col_con:
            return False
        return True

    def place(self, position: tuple, ship: str, ship_ind: int, direction: str = None) -> None:
        """Place a ship (variable 'ship' represents the type of ship) on the position where is the
        left end (direction = 'h') or top end (direction = 'v') of
        a ship placed on (or a certain position for submarine)."""
        # print(self)
        # print(position)
        # print(ship)
        # print(ship_ind)
        # print(self.ship_domain)
        assert position in self.ship_domain[ship][ship_ind]
        if ship != 'submarines' and direction is None:
            print('ERROR: argument \'direction\' is missing')
            return
        x = position[0]
        y = position[1]
        if ship == 'submarines':
            check_lst2 = [(x, y)]
            place_lst = ['S']
        elif ship == 'destroyers':
            # list for placing ship
            if direction == 'h':
                check_lst2 = [(x, y), (x + 1, y)]
                place_lst = ['L', 'R']
            else:
                check_lst2 = [(x, y), (x, y + 1)]
                place_lst = ['T', 'B']

        elif ship == 'cruisers':
            # list for placing ship
            if direction == 'h':
                check_lst2 = [(x, y), (x + 1, y), (x + 2, y)]
                place_lst = ['L', 'M', 'R']
            else:
                check_lst2 = [(x, y), (x, y + 1), (x, y + 2)]
                place_lst = ['T', 'M', 'B']

        elif ship == 'battleships':
            # list for placing ship
            if direction == 'h':
                check_lst2 = [(x, y), (x + 1, y), (x + 2, y), (x + 3, y)]
                place_lst = ['L', 'M', 'M', 'R']
            else:
                check_lst2 = [(x, y), (x, y + 1), (x, y + 2), (x, y + 3)]
                place_lst = ['T', 'M', 'M', 'B']
        else:
            return

        if not self.c_surrounding([ship, position, direction]):
            return
        if not self.c_row_col([ship, position, direction]):
            return

        # Place ship
        for i in range(len(check_lst2)):
            pos = check_lst2[i]
            self.map[pos] = place_lst[i]
        # Eliminate the domain of that ship and ship_seg
        for pos in check_lst2:
            if pos in self.ship_seg:
                self.ship_seg.pop(pos)
        self.ship_domain[ship].pop(ship_ind)
        self.ship_remain[ship] -= 1

    def check_constraints(self, ship1: list, ship2: list):
        global ship2_info
        for pos in self.ship_domain[ship2[0]][ship2[1]]:
            if ship2[0] == 'submarines':
                ship2_info = [ship2[0], pos]

                con_result = [self.c_row_col(ship2_info),
                              self.c_surrounding(ship2_info),
                              self.c_ships(ship1, ship2_info)]
                if all(con_result):
                    return True
            else:
                for direct in self.ship_domain[ship2[0]][ship2[1]][pos]:
                    ship2_info = [ship2[0], pos, direct]

                    con_result = [self.c_row_col(ship2_info),
                                  self.c_surrounding(ship2_info),
                                  self.c_ships(ship1, ship2_info)]
                    if all(con_result):
                        return True

        return False

    def c_row_col(self, ship: list) -> bool:
        """Return True if a given ship not offend the constraint of row and column.
        Otherwise, return False.
         - param:
            - ship: A list stores the information of ship:
            - index 0 represents the type of ship (string);
            - index 1 represents the position of top-end or left-end of the ship (tuple);
            - index 2 represents the direction of the ship (no index 2 if ship is submarine)
        """
        shape = len(self.row_con)
        ship_x = ship[1][0]
        ship_y = ship[1][1]
        row_lst = []
        col_lst = []
        row_lst.append([(x, ship_y) for x in range(shape)])
        col_lst.append([(ship_x, y) for y in range(shape)])
        if ship[0] == 'destroyers':
            if ship[2] == 'h':
                col_lst.append([(ship_x + 1, y) for y in range(shape)])
            else:
                row_lst.append([(x, ship_y + 1) for x in range(shape)])
        elif ship[0] == 'cruisers':
            if ship[2] == 'h':
                col_lst.append([(ship_x + 1, y) for y in range(shape)])
                col_lst.append([(ship_x + 2, y) for y in range(shape)])
            else:
                row_lst.append([(x, ship_y + 1) for x in range(shape)])
                row_lst.append([(x, ship_y + 2) for x in range(shape)])
        elif ship[0] == 'battleships':
            if ship[2] == 'h':
                col_lst.append([(ship_x + 1, y) for y in range(shape)])
                col_lst.append([(ship_x + 2, y) for y in range(shape)])
                col_lst.append([(ship_x + 3, y) for y in range(shape)])
            else:
                row_lst.append([(x, ship_y + 1) for x in range(shape)])
                row_lst.append([(x, ship_y + 2) for x in range(shape)])
                row_lst.append([(x, ship_y + 3) for x in range(shape)])

        # Start checking whether all rows and columns followed the constraints.
        ship_lst = self.ship_occupied(ship)
        for i in range(len(row_lst)):
            # Initiate and reset count
            row_count = 0
            for pos in row_lst[i]:
                if (self.map[pos] != '0' and self.map[pos] != 'W') or pos in ship_lst:
                    row_count += 1
            if not (row_count <= self.row_con[ship_y + i]):
                return False

        for i in range(len(col_lst)):
            # Initiate and reset count
            col_count = 0
            for pos in col_lst[i]:
                # If the space on game board both have a part of ship and
                # the given ship will occupied on it, we count it one time.
                # The correctness of this situation will be tested in other constraint.
                if (self.map[pos] != '0' and self.map[pos] != 'W') or pos in ship_lst:
                    col_count += 1
            if not (col_count <= self.col_con[ship_x + i]):
                return False

        return True

    def c_surrounding(self, ship: list) -> bool:
        """Return True if ship is not collide with the
        existed ship or part of ship on game board. Otherwise, return False.

         - param:
            - ship: A list stores the information of ship:
             - index 0 represents the type of ship (string);
             - index 1 represents the position of top-end or left-end of the ship (tuple);
             - index 2 represents the direction of the ship (no index 2 if ship is submarine)
        """
        shape = len(self.row_con)
        # Turn the spaces around ship into
        # np.array for checking whether it collides with map or not
        # (space is occupied represents 1,
        # and the one is not occupied represents 0).
        ship_field = self.np_ship(ship)
        # Turn the game board into np.array.
        state_field = self.np_state()

        # Checking whether ship complete any partial ship on the map:
        # if yes, then change that partial ship, on state_field, to 0.
        check_lst = self.ship_occupied(ship)
        seg_count = 0
        for i in range(len(check_lst)):
            key = check_lst[i]
            # Ship cannot be occupied on the spaces that ensure it is water
            if ship[0] == 'submarines':
                if self.map[key] != '0':
                    return False
            else:
                if self.map[key] == '0':
                    pass
                elif self.map[key] == 'W':
                    return False
                elif (self.map[key] == 'T' and ship[2] == 'v') \
                        or (self.map[key] == 'L' and ship[2] == 'h'):
                    if i != 0:
                        return False
                    else:
                        seg_count += 1
                        state_field[key[1]][key[0]] = 0
                elif (self.map[key] == 'B' and ship[2] == 'v') \
                        or (self.map[key] == 'R' and ship[2] == 'h'):
                    if i != (len(check_lst) - 1):
                        return False
                    else:
                        seg_count += 1
                        state_field[key[1]][key[0]] = 0
                elif self.map[key] == 'M':
                    if not (0 < i < (len(check_lst) - 1)):
                        return False
                    else:
                        seg_count += 1
                        state_field[key[1]][key[0]] = 0

        # Avoid the situation that ship occupied on a same pre-existed ship with same position.
        if seg_count == len(check_lst):
            # Eliminate the position in ship_seg, since ship segments already built a ship.
            for pos in check_lst:
                if pos in self.ship_seg:
                    self.ship_seg.pop(pos)
            return False

        return np.vdot(state_field, ship_field) == 0

    def c_ships(self, ship1: list, ship2: list) -> bool:
        """Return True if two ships has safe distance with each other.
         - param:
            - ship: A list stores the information of ship:
             - index 0 represents the type of ship (string);
             - index 1 represents the position of top-end or left-end of the ship (tuple);
             - index 2 represents the direction of the ship (no index 2 if ship is submarine)
        """
        shape = len(self.row_con)
        ship1_field = self.np_ship(ship1)
        ship2_occ = self.ship_occupied(ship2)
        ship2_field = np.zeros((shape, shape))
        for pos in ship2_occ:
            ship2_field[pos[1]][pos[0]] = 1

        return np.vdot(ship1_field, ship2_field) == 0

    def np_state(self):
        """Return an np.array for helping to compare a ship is valid for placing or not."""
        shape = len(self.row_con)
        result = np.zeros((shape, shape))
        for key in self.map:
            if self.map[key] != '0' and self.map[key] != 'W':
                result[key[1]][key[0]] = 1
        return result

    def np_ship(self, ship: list):
        """Return an np.array for helping to compare a ship is valid for placing or not.
        - param:
            - ship: A list stores the information of ship:
             - index 0 represents the type of ship (string);
             - index 1 represents the position of top-end or left-end of the ship (tuple);
             - index 2 represents the direction of the ship (no index 2 if ship is submarine)
        """
        shape = len(self.row_con)
        s_field = np.zeros((shape, shape))
        # Getting the position of spaces around the ship (included the space occupied by ship)
        if ship[0] == 'submarines':
            x_range = ship[1][0] + 2  # start from ship[1][1] - 1
            y_range = ship[1][1] + 2  # start from ship[1][1] - 1
            # ship1_field = [(x, y) for y in range(ship[1][1] - 1, ship[1][1] + 2)
            #                for x in range(ship[1][0] - 1, ship[1][0] + 2)
            #                if 0 <= x < shape and 0 <= y < shape]

        elif ship[0] == 'destroyers':
            if ship[2] == 'h':
                x_range = ship[1][0] + 3
                y_range = ship[1][1] + 2
            else:
                x_range = ship[1][0] + 2
                y_range = ship[1][1] + 3
        elif ship[0] == 'cruisers':
            if ship[2] == 'h':
                x_range = ship[1][0] + 4
                y_range = ship[1][1] + 2
            else:
                x_range = ship[1][0] + 2
                y_range = ship[1][1] + 4
        else:
            if ship[2] == 'h':
                x_range = ship[1][0] + 5
                y_range = ship[1][1] + 2
            else:
                x_range = ship[1][0] + 2
                y_range = ship[1][1] + 5

        for y in range(ship[1][1] - 1, y_range):
            for x in range(ship[1][0] - 1, x_range):
                if 0 <= x < shape and 0 <= y < shape:
                    s_field[y][x] = 1
        return s_field

    def ship_occupied(self, ship: list) -> list:
        """Return a list of coordinates that a given ship will occupied.
        """
        check_lst = []
        ship_x = ship[1][0]
        ship_y = ship[1][1]
        shape = len(self.row_con)
        if ship[0] == 'submarines':
            check_lst = [(x, y) for y in range(ship_y, ship_y + 1)
                         for x in range(ship_x, ship_x + 1)]
        elif ship[0] == 'destroyers':
            if ship[2] == 'h':
                check_lst = [(x, y) for y in range(ship_y, ship_y + 1)
                             for x in range(ship_x, ship_x + 2)]
            else:
                check_lst = [(x, y) for y in range(ship_y, ship_y + 2)
                             for x in range(ship_x, ship_x + 1)]
        elif ship[0] == 'cruisers':
            if ship[2] == 'h':
                check_lst = [(x, y) for y in range(ship_y, ship_y + 1)
                             for x in range(ship_x, ship_x + 3)]
            else:
                check_lst = [(x, y) for y in range(ship_y, ship_y + 3)
                             for x in range(ship_x, ship_x + 1)]
        elif ship[0] == 'battleships':
            if ship[2] == 'h':
                check_lst = [(x, y) for y in range(ship_y, ship_y + 1)
                             for x in range(ship_x, ship_x + 4)]
            else:
                check_lst = [(x, y) for y in range(ship_y, ship_y + 4)
                             for x in range(ship_x, ship_x + 1)]
        test_lst = [tup for tup in check_lst if 0 <= tup[0] < shape and 0 <= tup[1] < shape]
        assert check_lst == test_lst
        return check_lst


def s_clone(s: State) -> State:
    """
    Return a same State without aliasing.
    """
    clone = State()
    # Copy State
    clone.map = s.map.copy()
    clone.ship_remain = s.ship_remain.copy()
    clone.ship_seg = s.ship_seg.copy()
    clone.ship_domain = s.ship_domain.copy()
    clone.row_con = s.row_con.copy()
    clone.col_con = s.col_con.copy()
    for key in s.ship_domain:
        clone.ship_domain[key] = s.ship_domain[key].copy()
        if key != 'submarines':
            for i in s.ship_domain[key]:
                clone.ship_domain[key][i] = s.ship_domain[key][i].copy()
    return clone


def txt_to_state(file: str) -> State:
    """Return a State that convert input form to a game board state."""
    f = open(file, 'r')
    str_lst = f.readlines()
    s = State()
    shape = len(str_lst[0]) - 1  # Not include '\n'
    # Initiate the row and column constraints
    for i in range(shape):
        s.row_con.append(int(str_lst[0][i]))
    for i in range(shape):
        s.col_con.append(int(str_lst[1][i]))

    # Initiate the number of ships we need to place on the board
    for i in range(len(str_lst[2]) - 1):
        if i == 0:
            s.ship_remain['submarines'] = int(str_lst[2][i])
        elif i == 1:
            s.ship_remain['destroyers'] = int(str_lst[2][i])
        elif i == 2:
            s.ship_remain['cruisers'] = int(str_lst[2][i])
        else:
            s.ship_remain['battleships'] = int(str_lst[2][i])

    # Initiate the domain of each ship
    coor_lst = [(x, y) for y in range(shape) for x in range(shape)]
    for key in s.ship_remain:
        for i in range(s.ship_remain[key]):
            if key == 'submarines':
                # create a list with all coordinates can be placed on the map
                s.ship_domain[key][i] = []
                for coor in coor_lst:
                    s.ship_domain[key][i].append(coor)

            elif key == 'destroyers':
                # create a list with all coordinates can be placed on the map
                s.ship_domain[key][i] = dict()
                for coor in coor_lst:
                    x, y = coor
                    if 0 <= x < (shape - 1) and 0 <= y < (shape - 1):
                        # Both vertical and horizontal direction
                        s.ship_domain[key][i][coor] = ['h', 'v']
                    elif 0 <= y < (shape - 1):
                        # Only vertical direction
                        s.ship_domain[key][i][coor] = ['v']
                    elif 0 <= x < (shape - 1):
                        # Only horizontal direction
                        s.ship_domain[key][i][coor] = ['h']
            elif key == 'cruisers':
                s.ship_domain[key][i] = dict()
                for coor in coor_lst:
                    x, y = coor
                    if 0 <= x < (shape - 2) and 0 <= y < (shape - 2):
                        # Both vertical and horizontal direction
                        s.ship_domain[key][i][coor] = ['h', 'v']
                    elif 0 <= y < (shape - 2):
                        # Only vertical direction
                        s.ship_domain[key][i][coor] = ['v']
                    elif 0 <= x < (shape - 2):
                        # Only horizontal direction
                        s.ship_domain[key][i][coor] = ['h']
            else:
                s.ship_domain[key][i] = dict()
                for coor in coor_lst:
                    x, y = coor
                    if 0 <= x < (shape - 3) and 0 <= y < (shape - 3):
                        # Both vertical and horizontal direction
                        s.ship_domain[key][i][coor] = ['h', 'v']
                    elif 0 <= y < (shape - 3):
                        # Only vertical direction
                        s.ship_domain[key][i][coor] = ['v']
                    elif 0 <= x < (shape - 3):
                        # Only horizontal direction
                        s.ship_domain[key][i][coor] = ['h']

    # Initiate the game board
    for y_lst in range(shape):
        for x_lst in range(shape):
            s.map[(x_lst, y_lst)] = str_lst[y_lst + 3][x_lst]
            # Record the position of ship segments (not empty spot and not water)
            if s.map[(x_lst, y_lst)] != '0' and \
                    s.map[(x_lst, y_lst)] != 'W' and \
                    s.map[(x_lst, y_lst)] != 'S':
                s.ship_seg[(x_lst, y_lst)] = s.map[(x_lst, y_lst)]
            elif s.map[(x_lst, y_lst)] == 'S':
                s.ship_remain['submarines'] -= 1

    # Set the col/row to be all 'W' if its row/column constraint is 0.
    for i in range(len(s.row_con)):
        if s.row_con[i] == 0:
            # Set that row to 'W'
            for x in range(shape):
                s.map[(x, i)] = 'W'

    for i in range(len(s.col_con)):
        if s.col_con[i] == 0:
            # Set that column to 'W'
            for y in range(shape):
                s.map[(i, y)] = 'W'

    f.close()
    return s


def forward_check(s: State):
    """Return a solution state by using forward checking algorithm"""
    # Checking if the current state is a goal state
    zero_remain = 0
    for key in s.ship_remain:
        if s.ship_remain[key] == 0:
            zero_remain += 1
    if zero_remain == 4:
        print(s)
        return

    # Pick an unassigned variable and doing recursion
    # print(pick_var(s))
    ship_var = pick_var(s)
    if ship_var is None:
        return
    else:
        ship, ship_ind, directions = ship_var
    domain = []  # list of tuple stores positions
    if ship == 'submarines':
        domain = s.ship_domain[ship][ship_ind]
    else:
        for direct in directions:
            for pos in s.ship_domain[ship][ship_ind]:
                if direct in s.ship_domain[ship][ship_ind][pos]:
                    domain.append([pos, direct])

    for pos in domain:
        tmp_s = s_clone(s)
        if ship == 'submarines':
            tmp_s.place(pos, ship, ship_ind, directions)
            ship_info = [ship, pos]
        else:
            tmp_s.place(pos[0], ship, ship_ind, pos[1])
            ship_info = [ship, pos[0], pos[1]]
        if tmp_s == s:
            continue

        # Checking if the current state is a goal state
        zero_remain = 0
        for key in tmp_s.ship_remain:
            if tmp_s.ship_remain[key] == 0:
                zero_remain += 1
        if zero_remain == 4:
            for f_pos in tmp_s.map:
                if tmp_s.map[f_pos] == '0':
                    tmp_s.map[f_pos] = 'W'
            print(tmp_s)
            exit()

        dwo_occurred = False

        # Getting all the constraints with only one unassigned variable.
        c_queue = []
        for key in tmp_s.ship_domain:
            for i in tmp_s.ship_domain[key]:
                if key != ship or i != ship_ind:
                    c_queue.append([key, i])
        for c in c_queue:
            if not tmp_s.check_constraints(ship_info, c):
                dwo_occurred = True
                break

        if not dwo_occurred:
            forward_check(tmp_s)
        # Restore state
        # print(tmp_s)
        # print(tmp_s.ship_remain)
        tmp_s = s_clone(s)
    return


def pick_var(s: State) -> list:
    """ Return a list contains ship type, ship index, and ship direction for
    picking an unassigned variable for forward checking or GAC.
     - priority 1: Pick a ship that can complete the ship_segment with
     the lowest constraint mark (the number of row and column constraint at that position).
     - priority 2: Pick the largest ship
    """
    shape = len(s.row_con)
    pick_list = []
    directions = None
    if len(s.ship_seg) > 0:
        # Find the one with lowest constraint mark
        lowest_seg = None
        lowest_mark = None
        for pos in s.ship_seg:
            mark = s.row_con[pos[1]] + s.col_con[pos[0]]
            if lowest_mark is None or lowest_mark > mark:
                lowest_seg = pos
                lowest_mark = mark

        # Find what the biggest possible ship
        # Getting a list of ship from largest to smallest
        if s.ship_seg[lowest_seg] == 'T':
            directions = ['v', 'h']
            if s.col_con[lowest_seg[0]] >= 4 and (shape - 1 - lowest_seg[1]) >= 3:
                pick_list = ['battleships', 'cruisers', 'destroyers']
            elif s.col_con[lowest_seg[0]] >= 3 and (shape - 1 - lowest_seg[1]) >= 2:
                pick_list = ['cruisers', 'destroyers']
            elif s.col_con[lowest_seg[0]] >= 2 and (shape - 1 - lowest_seg[1]) >= 1:
                pick_list = ['destroyers']
        elif s.ship_seg[lowest_seg] == 'B':
            directions = ['v', 'h']
            if s.col_con[lowest_seg[0]] >= 4 and lowest_seg[1] >= 3:
                pick_list = ['battleships', 'cruisers', 'destroyers']
            elif s.col_con[lowest_seg[0]] >= 3 and lowest_seg[1] >= 2:
                pick_list = ['cruisers', 'destroyers']
            elif s.col_con[lowest_seg[0]] >= 2 and lowest_seg[1] >= 1:
                pick_list = ['destroyers']
        elif s.ship_seg[lowest_seg] == 'L':
            directions = ['h', 'v']
            position = (lowest_seg[0], lowest_seg[1])
            if s.row_con[lowest_seg[1]] >= 4 and (shape - 1 - lowest_seg[0]) >= 3:
                pick_list = ['battleships', 'cruisers', 'destroyers']
            elif s.row_con[lowest_seg[1]] >= 3 and (shape - 1 - lowest_seg[0]) >= 2:
                pick_list = ['cruisers', 'destroyers']
            elif s.row_con[lowest_seg[1]] >= 2 and (shape - 1 - lowest_seg[0]) >= 1:
                pick_list = ['destroyers']
        elif s.ship_seg[lowest_seg] == 'R':
            directions = ['h', 'v']
            if s.row_con[lowest_seg[1]] >= 4 and lowest_seg[0] >= 3:
                pick_list = ['battleships', 'cruisers', 'destroyers']
            elif s.row_con[lowest_seg[1]] >= 3 and lowest_seg[0] >= 2:
                pick_list = ['cruisers', 'destroyers']
            elif s.row_con[lowest_seg[1]] >= 2 and lowest_seg[0] >= 1:
                pick_list = ['destroyers']
        elif s.ship_seg[lowest_seg] == 'M':
            if s.row_con[lowest_seg[1]] >= s.col_con[lowest_seg[0]]:
                directions = ['h', 'v']
                if s.row_con[lowest_seg[1]] >= 4:
                    pick_list = ['battleships', 'cruisers']
                else:
                    pick_list = ['cruisers']
            else:
                directions = ['v', 'h']
                if s.col_con[lowest_seg[0]] >= 4:
                    pick_list = ['battleships', 'cruisers']
                else:
                    pick_list = ['cruisers']
    else:
        # If there is no ship segment on the game board,
        # then find the largest ship
        pick_list = ['battleships', 'cruisers', 'destroyers', 'submarines']
    for ship in pick_list:
        remain = s.ship_remain[ship]
        if remain > 0:
            if directions is None and ship != 'submarines':
                # Find the one with lowest domain
                h_count = 0
                v_count = 0
                for key in s.ship_domain[ship][remain - 1]:
                    if 'h' in s.ship_domain[ship][remain - 1][key]:
                        h_count += 1
                    if 'v' in s.ship_domain[ship][remain - 1][key]:
                        v_count += 1
                if h_count >= v_count:
                    directions = ['h', 'v']
                else:
                    directions = ['v', 'h']
            return [ship, remain - 1, directions]


if __name__ == "__main__":
    state = txt_to_state('input_hard1.txt')
    # tmp_s = s_clone(state)
    # print(tmp_s == state)
    forward_check(state)
