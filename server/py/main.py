from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import json
import asyncio

import server.py.hangman as hangman
import server.py.battleship as battleship
import server.py.dog as dog

import random

app = FastAPI()

app.mount("/inc/static", StaticFiles(directory="server/inc/static"), name="static")

templates = Jinja2Templates(directory="server/inc/templates")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ----- Hangman -----

@app.get("/hangman/singleplayer/local/", response_class=HTMLResponse)
async def hangman_singleplayer(request: Request):
    return templates.TemplateResponse("game/hangman/singleplayer_local.html", {"request": request})

@app.websocket("/hangman/singleplayer/ws")
async def hangman_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()

    idx_player_you = 0

    try:

        game = hangman.Hangman()

        words = []
        with open('server/py/hangman_words.json') as fin:
            words = json.load(fin)
        word_to_guess = random.choice(words)

        state = hangman.HangmanGameState(word_to_guess=word_to_guess, phase=hangman.GamePhase.RUNNING, guesses=[], incorrect_guesses=[])
        game.set_state(state)

        while True:

            state = game.get_player_view(idx_player_you)

            game.print_state()

            state = game.get_player_view(idx_player_you)
            list_action = game.get_list_action()
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = [action.model_dump() for action in list_action]
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)

            if state.phase == hangman.GamePhase.FINISHED:
                break

            if len(list_action) == 0:
                game.apply_action(None)
            else:
                data = await websocket.receive_json()
                if data['type'] == 'action':
                    action = hangman.GuessLetterAction.model_validate(data['action'])
                    game.apply_action(action)
                    print(action)

            continue
            state = game.get_player_view(idx_player_you)
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []

            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)

    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- Battleship -----

@app.get("/battleship/simulation/", response_class=HTMLResponse)
async def battleship_simulation(request: Request):
    return templates.TemplateResponse("game/battleship/simulation.html", {"request": request})


@app.websocket("/battleship/simulation/ws")
async def battleship_simulation_ws(websocket: WebSocket):
    await websocket.accept()

    idx_player_you = 0

    try:
        game = battleship.Battleship()
        player = battleship.RandomPlayer()

        while True:

            state = game.get_state()
            list_action = game.get_list_action()
            action = None
            if len(list_action) > 0:
                action = player.select_action(state, list_action)

            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []
            dict_state['selected_action'] = None if action is None else action.model_dump()
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)

            if state.phase == battleship.GamePhase.FINISHED:
                break

            data = await websocket.receive_json()

            if data['type'] == 'action':
                action = battleship.BattleshipAction.model_validate(data['action'])
                game.apply_action(action)

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/battleship/singleplayer", response_class=HTMLResponse)
async def battleship_singleplayer(request: Request):
    return templates.TemplateResponse("game/battleship/singleplayer.html", {"request": request})


@app.websocket("/battleship/singleplayer/ws")
async def battleship_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()

    idx_player_you = 0

    try:

        game = battleship.Battleship()
        player = battleship.RandomPlayer()

        while True:

            state = game.get_state()
            if state.phase == battleship.GamePhase.FINISHED:
                break

            #game.print_state()

            if state.idx_player_active == idx_player_you:

                state = game.get_player_view(idx_player_you)
                list_action = game.get_list_action()
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = [action.model_dump() for action in list_action]
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

                if len(list_action) == 0:
                    game.apply_action(None)
                else:
                    data = await websocket.receive_json()
                    if data['type'] == 'action':
                        action = battleship.BattleshipAction.model_validate(data['action'])
                        game.apply_action(action)
                        print(action)

                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []

                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

            else:

                state = game.get_player_view(state.idx_player_active)
                list_action = game.get_list_action()
                action = player.select_action(state, list_action)
                if action is not None:
                    await asyncio.sleep(1)
                game.apply_action(action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- UNO -----

@app.get("/uno/simulation/", response_class=HTMLResponse)
async def uno_simulation(request: Request):
    return templates.TemplateResponse("game/uno/simulation.html", {"request": request})


@app.websocket("/uno/simulation/ws")
async def uno_simulation_ws(websocket: WebSocket):
    await websocket.accept()

    try:

        pass

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/uno/singleplayer", response_class=HTMLResponse)
async def uno_singleplayer(request: Request):
    return templates.TemplateResponse("game/uno/singleplayer.html", {"request": request})


@app.websocket("/uno/singleplayer/ws")
async def uno_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()

    try:

        pass

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.websocket("/uno/random_player/ws")
async def uno_random_player_ws(websocket: WebSocket):
    await websocket.accept()

    try:

        pass

    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- Dog -----


@app.get("/dog/simulation/", response_class=HTMLResponse)
async def dog_simulation(request: Request):
    return templates.TemplateResponse("game/dog/simulation.html", {"request": request})


@app.websocket("/dog/simulation/ws")
async def dog_simulation_ws(websocket: WebSocket):
    await websocket.accept()
    
    """
    This endpoint handles a fully automated Dog game, 
    where the RandomPlayer class simulates actions for all players.
    """
    
    try:
        #Initialize Dog game and random player AI
        game = dog.Dog()
        player = dog.RandomPlayer()
        
        while True: 
            #get current state of the game
            state = game.get_state()
            list_action = game.get_list_action()
            
            #if there are valid action, random player can pick one
            action = None
            if len(list_action) > 0:
                action = player.select_action(state, list_action)

            # Prepare the state to send to the client
            dict_state = state.model_dump()
            dict_state['list_action'] = []  # We don't send possible actions in the simulation mode
            dict_state['selected_action'] = None if action is None else action.model_dump()
            
            data = {'type': 'update', 'state' : dict_state}
            await websocket.send_json(data) # Send the updated state to the client
            
            # Break the loop if the game is finished
            if state.phase == dog.GamePhase.FINISHED:
                break
            
            # Apply the action and continue the game loop
            game.apply_action(action)

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/dog/singleplayer", response_class=HTMLResponse)
async def dog_singleplayer(request: Request):
    return templates.TemplateResponse("game/dog/singleplayer.html", {"request": request})


@app.websocket("/dog/singleplayer/ws")
async def dog_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()
    
    """
    This endpoint allows the user to play as one of the players in the Dog game
    while the other players are controlled by AI.
    """

    idx_player_you = 0 # Assigns the user as Player 0

    try:
        # Initialize Dog game and random palyer ai
        game = dog.Dog()
        print(f"Initialized Game State: {game.get_state().model_dump()}") # for debuging
        player = dog.RandomPlayer()

        while True:
            state = game.get_state()

            if state.phase == dog.GamePhase.FINISHED:
                print("Game Finished.") # for debuging
                break

            if state.idx_player_active == idx_player_you:
                # It's the user's turn
                state = game.get_player_view(idx_player_you)  
                list_action = game.get_list_action()

                dict_state = state.model_dump()
                dict_state['list_action'] = [action.model_dump() for action in list_action]
                dict_state['idx_player_you'] = idx_player_you
                print(f"Sending State to Client: {dict_state}") # for debuging

                # Send the updated state to the client
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

                if len(list_action) == 0:
                    # If no actions are available, move to the next player
                    game.apply_action(None)
                    print(f"Updated Game State (No Actions): {game.get_state().model_dump()}")# for debug
                else:
                    # Receive the action from the client
                    data = await websocket.receive_json()
                    print(f"Received Data from Client: {data}") # for debug
                    if data['type'] == 'action':
                        action = dog.Action.model_validate(data['action'])
                        print(f"Applying Action: {action.model_dump()}") # for debug
                        game.apply_action(action)
                        print(f"Updated Game State: {game.get_state().model_dump()}") # for debug


            else:
                # It's the AI's turn
                list_action = game.get_list_action()
                action = player.select_action(state, list_action)
                print(f"AI Selected Action: {action.model_dump() if action else None}") #for debug
                game.apply_action(action)
                print(f"Updated Game State (AI Turn): {game.get_state().model_dump()}")# for debug

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.websocket("/dog/random_player/ws")
async def dog_random_player_ws(websocket: WebSocket):
    await websocket.accept()
# Not sure why this is needed at the moment

    try:
    
        pass

    except WebSocketDisconnect:
        print('DISCONNECTED')
