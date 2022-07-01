import pygame
import sys
import socket
import easygui
from random import choice

class Piece:
    def __init__(self, name):
        self.name = name
        self.type = name[1:]
        self.side = 1 if name.lower().startswith("b") else -1
        self.img = pygame.image.load("./images/" + name + ".png")
        self.enpassant = False

class Button:
    def __init__(self, param, path, name):
        self.x, self.y = param
        self.name = name
        self.img = pygame.image.load(path)
 
    def show(self, surface):
        surface.blit(self.img, (self.x, self.y))
 
    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.img.get_rect().collidepoint(x - self.x, y - self.y):
                if self.name == "Host":
                    initAsHost()
                    return
                if self.name == "Join":
                    initAsJoin()
                    return
                if self.name == "Local":
                    initAsLocal()
                    return

# game variables
screen_size = 1000
scale = screen_size / 8
grid = [
    [Piece("brook"), Piece("bhorse"), Piece("bbishop"), Piece("bking"), Piece("bqueen"), Piece("bbishop"), Piece("bhorse"), Piece("brook")],
    [Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn")],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn")],
    [Piece("wrook"), Piece("whorse"), Piece("wbishop"), Piece("wking"), Piece("wqueen"), Piece("wbishop"), Piece("whorse"), Piece("wrook")]
]
black_won = "./images/black_won.png"
white_won = "./images/white_won.png"
sel = [-1, -1]
current_player = -1
winner = False
multiplayer_player_number = None

# title screen variables
host_button = Button((40, 700), "./images/host_button.png", "Host")
join_button = Button((1000 - 325 - 40, 700), "./images/join_button.png", "Join")
local_button = Button((500 - 174, 850), "./images/local_button.png", "Local")
title_screen_img = pygame.image.load("./images/titlescreen.png")

# initialisations
title_screen = True
mode = None
pygame.init()
display = pygame.display.set_mode(size=(screen_size, screen_size))
display.fill((100, 100, 100))

# -----------------------------------------------------------------------------------------------------------------------------------
# ---------------FUNCTIONS-----------------------------FUNCTIONS-----------------------------------FUNCTIONS-------------------------
# -----------------------------------------------------------------------------------------------------------------------------------

# game functions
def drawGrid(invert = False):
    if invert:
        for y, line in enumerate(reversed(grid)):
            for x, element in enumerate(reversed(line)):
                if 7 - sel[0] == x and 7 - sel[1] == y:
                    color = (255, 255, 40)
                elif (x - (y % 2)) % 2 == 0:
                    color = (150, 150, 150)
                else:
                    color = (100, 100, 100)
                pygame.draw.rect(display, color, pygame.rect.Rect(x * scale, y * scale, scale, scale))
                if element != None:
                    display.blit(pygame.transform.scale(element.img, (scale, scale)), (x * scale, y * scale))
    else:
        for y, line in enumerate(grid):
            for x, element in enumerate(line):
                if sel[0] == x and sel[1] == y:
                    color = (255, 255, 40)
                elif (x - (y % 2)) % 2 == 0:
                    color = (150, 150, 150)
                else:
                    color = (100, 100, 100)
                pygame.draw.rect(display, color, pygame.rect.Rect(x * scale, y * scale, scale, scale))
                if element != None:
                    display.blit(pygame.transform.scale(element.img, (scale, scale)), (x * scale, y * scale))

def registerClick(invert = False):
    global sel, game_over, winner, title_screen

    if type(winner) != bool:
        reset()
        title_screen = True
        return

    if mode != "Local" and multiplayer_player_number != current_player:
        return

    # get mouse coordinates and translate to grid index
    x, y = pygame.mouse.get_pos()
    x = int(x / scale)
    y = int(y / scale)

    if invert:
        x = 7 - x
        y = 7 - y

    # exit if same field
    if x == sel[0] and y == sel[1]:
        sel = [-1, -1]
        return

    # set selection or try to make move and reset selection
    # set
    if sel[0] < 0 and sel[0] < 0:
        # set selection if field not none
        if grid[y][x] != None:
            # exit if wrong color
            if grid[y][x].side != current_player:
                return
            # set selection
            sel = [x, y]
    # move
    else:
        winner = move(x, y)
        if mode == "Host" and winner != False:
            c.send(bytearray((str(sel[0]) + ", " + str(sel[1]) + ", " + str(x) + ", " + str(y)).encode()))
        if mode == "Join" and winner != False:
            s.send(bytearray((str(sel[0]) + ", " + str(sel[1]) + ", " + str(x) + ", " + str(y)).encode()))
        sel = [-1, -1]

def move(x, y):
    global sel, current_player

    piece = grid[sel[1]][sel[0]]
    valid_move = False
    is_king = True if grid[y][x] != None and grid[y][x].type == "king" else False

    # Pawn
    if piece.type == "pawn":
        if sel[1] * piece.side < y * piece.side:
            # filter diagonal moves
            if x == sel[0] - 1 and y == sel[1] + piece.side:
                if grid[y][x] != None and grid[y][x].side != piece.side:
                    valid_move = makeMove(x, y)
                if grid[y][x] == None and grid[y - piece.side][x] != None and grid[y - piece.side][x].enpassant:
                    valid_move = makeMove(x, y)
                    grid[y - piece.side][x] = None
            if x == sel[0] + 1 and y == sel[1] + piece.side:
                if grid[y][x] != None and grid[y][x].side != piece.side:
                    valid_move = makeMove(x, y)
                if grid[y][x] == None and grid[y - piece.side][x] != None and grid[y - piece.side][x].enpassant:
                    valid_move = makeMove(x, y)
                    grid[y - piece.side][x] = None
            # filter vertical moves
            if sel[0] == x:
                # allow one field forward, if piece stands on its original position allow 2
                if abs(sel[1] * piece.side - y * piece.side) <= (2 if (sel[1] == 1 and piece.side == 1 or sel[1] == 6 and piece.side == -1) and grid[sel[1] + piece.side][x] == None else 1):
                    # exit if field in front is not empty
                    if grid[y][x] != None:
                        return False
                    # do the setting
                    valid_move = makeMove(x, y)
                    if abs(sel[1] - y) == 2:
                        grid[y][x].enpassant = True
        # change to queen if on last rank
        if valid_move and (y == 0 or y == 7):
            grid[y][x] = Piece(piece.name[:1] + "queen")
    
    # Rook
    if piece.type == "rook":
        if sel[0] == x:
            for i in range(min(sel[1], y) + 1, max(sel[1], y)):
                if grid[i][x] != None:
                    return False
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)
        if sel[1] == y:
            for i in range(min(sel[0], x) + 1, max(sel[0], x)):
                if grid[y][i] != None:
                    return False
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)

    # Bishop
    if piece.type == "bishop":
        if abs(sel[0] - x) == abs(sel[1] - y):
            x_dir = int((x - sel[0]) / abs(x - sel[0]))
            y_dir = int((y - sel[1]) / abs(y - sel[1]))

            for i in range(1, abs(sel[0] - x)):
                if grid[sel[1] + i * y_dir][sel[0] + i * x_dir] != None:
                    return False
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)

    # Horse
    if piece.type == "horse":
        if abs(sel[1] - y) == 2 and abs(sel[0] - x) == 1 or abs(sel[1] - y) == 1 and abs(sel[0] - x) == 2:
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)

    # King
    if piece.type == "king":
        if abs(sel[1] - y) <= 1 or abs(sel[0] - x) <= 1:
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)

    # Queen
    if piece.type == "queen":
        if abs(sel[0] - x) == abs(sel[1] - y):
            x_dir = int((x - sel[0]) / abs(x - sel[0]))
            y_dir = int((y - sel[1]) / abs(y - sel[1]))

            for i in range(1, abs(sel[0] - x)):
                if grid[sel[1] + i * y_dir][sel[0] + i * x_dir] != None:
                    return False
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)
        if sel[0] == x:
            for i in range(min(sel[1], y) + 1, max(sel[1], y)):
                if grid[i][x] != None:
                    return False
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)
        if sel[1] == y:
            for i in range(min(sel[0], x) + 1, max(sel[0], x)):
                if grid[y][i] != None:
                    return False
            if grid[y][x] != None and grid[y][x].side == piece.side:
                return False
            valid_move = makeMove(x, y)

    if valid_move:
        # check for win
        if is_king:
            print("White has won!" if grid[y][x].side == -1 else "Black has won!")
            return pygame.image.load(white_won) if grid[y][x].side == -1 else pygame.image.load(black_won)
        # switch player
        current_player = -current_player

        for line in grid:
            for element in line:
                if element != None and element.side == current_player:
                    element.enpassant = False

    return valid_move
    
def makeMove(x, y):
    grid[y][x] = grid[sel[1]][sel[0]]
    grid[sel[1]][sel[0]] = None
    return True

def drawGame(invert = False):
    drawGrid(invert=invert)
    if type(winner) != bool:
        display.blit(pygame.transform.scale(winner, (screen_size, screen_size)), (0, 0))

def reset():
    global grid, current_player, sel, winner, multiplayer_player_number
    
    try:
        c.close()
    except:
        pass
    if not mode == "Local":
        s.close()
    grid = [
        [Piece("brook"), Piece("bhorse"), Piece("bbishop"), Piece("bking"), Piece("bqueen"), Piece("bbishop"), Piece("bhorse"), Piece("brook")],
        [Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn"), Piece("bpawn")],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn"), Piece("wpawn")],
        [Piece("wrook"), Piece("whorse"), Piece("wbishop"), Piece("wking"), Piece("wqueen"), Piece("wbishop"), Piece("whorse"), Piece("wrook")]
    ]
    sel = [-1, -1]
    current_player = -1
    winner = False
    multiplayer_player_number = None

# server functions
def drawTitleScreen():
    display.blit(title_screen_img, (0,0))
    host_button.show(display)
    join_button.show(display)
    local_button.show(display)

def loginClick(event):
    host_button.click(event)
    join_button.click(event)
    local_button.click(event)

def initAsHost():
    global host, port, s, title_screen, c, addr, multiplayer_player_number, mode

    mode = "Host"
    s = socket.socket()
    host = socket.gethostname()
    port = 12396
    s.bind(('',port))
    print("Hosting server. Waiting for client ...")
    s.listen(1)
    c, addr = s.accept()
    print("Got connection from" + str(addr))
    multiplayer_player_number = choice([-1, 1])
    print("I am player " + str(multiplayer_player_number))
    c.send((multiplayer_player_number + 1).to_bytes(1, 'big'))
    title_screen = False

def initAsJoin():
    global host, port, s, title_screen, multiplayer_player_number, mode
    
    mode = "Join"
    s = socket.socket()

    host = easygui.enterbox(title="IP Configuration:", default="192.168.0.1", msg="Enter ip adress: ")
    port = 12396
    
    try:
        s.connect((host,port))
        multiplayer_player_number = 1 if int.from_bytes(s.recv(1024), 'big') == 0 else -1
        print("I am player " + str(multiplayer_player_number))
        title_screen = False
    except ConnectionRefusedError:
        easygui.exceptionbox(title="IP not found!", msg="We can't find a server with this ip adress!")
    except OSError:
        easygui.exceptionbox(title="OS Error", msg="There is no host with this ip adress in your network!")

def initAsLocal():
    global title_screen, mode

    mode = "Local"
    title_screen = False

# -----------------------------------------------------------------------------------------------------------------------------------
# ---------------MAIN CODE-----------------------------MAIN CODE-----------------------------------MAIN CODE-------------------------
# -----------------------------------------------------------------------------------------------------------------------------------

while True:
    if title_screen:
        drawTitleScreen()
    else:
        drawGame(True if multiplayer_player_number == 1 else False)
    pygame.display.update()
    if multiplayer_player_number != current_player and type(winner) == bool:
        if mode == "Host":
            try:
                data = c.recv(1024).decode().split(", ")
                sel = [int(data[0]), int(data[1])]
                winner = move(int(data[2]), int(data[3]))
                sel = [-1, -1]
            except:
                c.close()
                s.close()
        if mode == "Join":
            try:
                data = s.recv(1024).decode().split(", ")
                sel = [int(data[0]), int(data[1])]
                winner = move(int(data[2]), int(data[3]))
                sel = [-1, -1]
            except:
                s.close()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if not mode == "Local":
                s.close()
            try:
                c.close()
            except:
                pass
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not title_screen:
                registerClick(True if multiplayer_player_number == 1 else False)
            else:
                loginClick(event)