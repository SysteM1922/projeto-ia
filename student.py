"""Example client."""
import asyncio
import getpass
import json
import os
import time
from test import search

# Next 4 lines are not needed for AI agents, please remove them from your code!
import websockets
from collections import defaultdict, deque


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        moves = deque([])
        boards = deque([])
        board = None
        current_level = ""
        t = time.perf_counter()
        while True:
            try:
                if moves:
                    [await websocket.recv() and print("Desync") for _ in range(int((time.perf_counter() - t)//0.1))]                        
                    move = moves.popleft()
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": move})
                    )  # send key command to server - you must implement this send in the AI agent
                state = json.loads(
                    await websocket.recv()
                )
                t = time.perf_counter()
                # receive game update, this must be called timely or your game will get out of sync with the server
                # get the vector of the car moved between the 2 last states
                level = state["grid"].split()[1]

                if moves:
                    continue

                # if the level has changed, we need to find the correct path
                if not boards or current_level != state["level"]:
                    board = level
                    current_level = state["level"]
                    size = state["dimensions"][0]
                    size_square = size ** 2

                    boards = search(level, size)

                # if a crazy car is blocking the way, we need to find the correct path
                if board != level:

                    def cannot_continue():
                        for i in range(size_square):
                            if board[i] == "o" and boards[0][i] not in "ox":
                                if level[i] != "o":
                                    return True
                                return False

                    if level in boards:
                        {boards.popleft() for _ in range(boards.index(level))}
                    elif cannot_continue():
                        car_b = defaultdict(list)
                        for i in range(size_square):
                            if boards[0][i] not in "ox":
                                car_b[boards[0][i]].append((i % size, i // size))

                        # new heuristic for the A* algorithm
                        def correct_heuristic(level, size):
                            car_l = defaultdict(list)
                            for i in range(size_square):
                                if boards[0][i] not in "ox":
                                    car_l[boards[0][i]].append((i % size, i // size))
                            # manhattan distance
                            return sum(
                                abs(car_b[car][0][0] - car_l[car][0][0])
                                + abs(car_b[car][0][1] - car_l[car][0][1])
                                for car in car_b
                            )

                        # new goal check for the A* algorithm
                        def correct_check_goal(level, size):
                            return level == boards[0]

                        boards = (
                            search(level, size, correct_check_goal, correct_heuristic)
                            + boards
                        )
                    else:
                        level = board

                if boards:    
                    board = boards.popleft()
                    a = []
                    b = []
                    car = ""
                    for i in range(size_square):
                        if level[i] != board[i]:
                            if level[i] not in "ox": 
                                a.append((i%size, i//size))
                                car = level[i]
                            if board[i] not in "ox":
                                b.append((i%size, i//size))

                # move cursor and select car if needed
                c = state.get("cursor")
                if car != "":
                    if state["selected"] != car:
                        if state["selected"] != "":
                            moves.append(" ")
                        if a[0][0] < c[0]:
                            moves += ["a" for _ in range(c[0]-a[0][0])]
                        if a[0][0] > c[0]:
                            moves += ["d" for _ in range(a[0][0]-c[0])]
                        if a[0][1] < c[1]:
                            moves += ["w" for _ in range(c[1]-a[0][1])]
                        if a[0][1] > c[1]:
                            moves += ["s" for _ in range(a[0][1]-c[1])]
                        moves.append(" ")
                    if a[0][1] > b[0][1]:
                        moves.append("w")
                    elif a[0][1] < b[0][1]:
                        moves.append("s")
                    elif a[0][0] > b[0][0]:
                        moves.append("a")
                    elif a[0][0] < b[0][0]:
                        moves.append("d")
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
