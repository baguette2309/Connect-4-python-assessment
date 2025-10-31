import pygame

pygame.init()
pygame.font.init()
pygame.mixer.init()

screen_width = 800
screen_height = 650
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Connect 4")

font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 60)

pygame.mixer.music.set_volume(0.2)

ui_hover = pygame.mixer.Sound("sounds/ui_mouse_hover.mp3")
token_place = pygame.mixer.Sound("sounds/token_place.mp3")
win_sound = pygame.mixer.Sound("sounds/tada_win.mp3")

ui_hover.set_volume(0.6)
win_sound.set_volume(0.6)

circle_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

ROWS = 7
COLUMNS = 6
GRID = []

column_positions = []
row_positions = []

bottom_positions = [5, 11, 17, 23, 29, 35, 41]
top_positions = [0, 6, 12, 18, 24, 30, 36]
left_positions = [0, 1, 2, 3, 4, 5]
right_positions = [36, 37, 38, 39, 40, 41]

player_colors = ["Red", "Yellow"]
hologram_colors = [(255, 0, 0, 128), (255, 220, 0, 128)]

# Create the foundation of the game and the grid list
def initialize():
    GRID.clear()
    size = 100
    for row in range(ROWS):
        x = 0
        for col in range(COLUMNS):
            x = row * size + size
            y = col * size + size/2

            GRID.append(0)
            if not int(y) in row_positions:
                row_positions.append(int(y))
        column_positions.append(x)

# Button class to make buttons easily
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.action = action
        self.font = font
        self.visible = False

    def draw(self):
        pygame.draw.rect(screen, self.current_color, self.rect)
        button_text = self.font.render(self.text, True, (0, 0, 0))
        button_center = button_text.get_rect(center=self.rect.center)
        screen.blit(button_text, button_center)
        self.visible = True

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(mouse_pos):
                if self.current_color != self.hover_color and self.visible:
                    ui_hover.play()
                self.current_color = self.hover_color
            else:
                self.current_color = self.color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(mouse_pos) and self.action:
                    self.action()

# InputBox class to make the input boxes easily (same case as button)
class InputBox:
    def __init__(self, x, y, width, height, ghost_text, color, interact_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.input_text = font.render(self.text, True, (0, 0, 0))
        self.ghost_text = ghost_text
        self.color = color
        self.interact_color = interact_color
        self.current_color = color
        self.font = font
        self.font_size = 30
        self.active = False
        self.allowed_characters = "abcdefghijklmnopqrstuvwxyz1234567890_"

    def draw(self):
        pygame.draw.rect(screen, self.current_color, self.rect)

        self.input_text = self.font.render(self.text, True, (0, 0, 0))
        if self.text == "" and not self.active:
            self.input_text = self.font.render(self.ghost_text, True, (0, 0, 0))

        input_center = self.input_text.get_rect(center=self.rect.center)
        screen.blit(self.input_text, input_center)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION and not self.active:
            if self.rect.collidepoint(mouse_pos):
                if self.current_color != self.interact_color:
                    ui_hover.play()
                self.current_color = self.interact_color
            else:
                self.current_color = self.color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(mouse_pos):
                    self.active = True
                    self.current_color = self.interact_color
                else:
                    self.active = False
                    self.current_color = self.color
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.current_color = self.color
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

                # Makes text bigger if it will not flow out of the box
                while self.input_text.get_width() < self.rect.width - 30 and self.font_size < 30:
                        self.font_size += 1
                        self.font = pygame.font.SysFont("Arial", self.font_size)
                        self.input_text = self.font.render(self.text, True, (0, 0, 0))
            else:
                if event.unicode.lower() in self.allowed_characters and len(self.text) + 1 <= 15:
                    self.text += event.unicode

                    # Makes text smaller if it will flow out of the box
                    while self.input_text.get_width() > self.rect.width - 30:
                        self.font_size -= 1
                        self.font = pygame.font.SysFont("Arial", self.font_size)
                        self.input_text = self.font.render(self.text, True, (0, 0, 0))

# The scene manager class handles which scene is currently active. Draws and handles events based on those scenes
class SceneManager:
    def __init__(self):
        self.current = None
        self.next_scene = None
        self.running = True

    def update(self):
        if self.next_scene:
            self.current = self.next_scene
            self.next_scene = None

    # Game loop
    def loop(self):
        while self.running:
            self.update()

            self.current.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.current.handle_event(event)

            pygame.display.update()

    def run(self, scene):
        self.current = scene
        self.loop()

scene_manager = SceneManager()

# The main menu scene
class MainMenu:
    def __init__(self):
        self.title_text = big_font.render("Connect 4", True, (0, 0, 0))
        self.start_button = Button(screen_width/2-80, screen_height/2-35, 160, 70, "Start Game", (255, 255, 255), (150, 150, 150), self.start_game)
        self.quit_button = Button(screen_width - 70, 10, 60, 50, "Quit", (255, 0, 0), (200, 0, 0), self.quit_game)
        self.p1_name_box = InputBox(screen_width/2-280, screen_height/2+100, 260, 70, "Player 1 (Red) name", (255, 255, 255), (150, 150, 150))
        self.p2_name_box = InputBox(screen_width/2+20, screen_height/2+100, 260, 70, "Player 2 (Yellow) name", (255, 255, 255), (150, 150, 150))
        pygame.mixer.music.load("sounds/Clair_de_Lune.mp3")
        pygame.mixer.music.play(-1)

    def start_game(self):
        initialize()
        pygame.mixer.music.load("sounds/Moonlight_Sonata_3rd.mp3")
        pygame.mixer.music.play(-1)
        scene_manager.next_scene = MainGame(self.p1_name_box.text, self.p2_name_box.text)
    
    def quit_game(self):
        scene_manager.running = False

    def draw(self):
        screen.fill((0, 120, 120))
        self.start_button.draw()
        self.quit_button.draw()
        self.p1_name_box.draw()
        self.p2_name_box.draw()
        screen.blit(self.title_text, (screen_width/2 - self.title_text.get_width()/2, screen_height/2 - 150))

        pygame.display.update()

    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.quit_button.handle_event(event)
        self.p1_name_box.handle_event(event)
        self.p2_name_box.handle_event(event)

# The main game scene
class MainGame:
    def __init__(self, p1_name, p2_name):
        self.player_turn = 1
        self.target_grid = None
        self.win = False
        self.tie = False
        self.restart_button = Button(screen_width/2 - 80, screen_height/2 - 35, 160, 70, "Rematch", (255, 255, 255), (150, 150, 150), self.restart_match)
        self.mainmenu_button = Button(screen_width/2 - 80, screen_height/2 + 70, 160, 70, "Main menu", (255, 255, 255), (150, 150, 150), self.return_to_menu)
        self.player_names = [p1_name, p2_name]
        self.clock = pygame.time.Clock()
        self.time = 0
        self.end_time = 0

    def return_to_menu(self):
        scene_manager.next_scene = MainMenu()
    
    def restart_match(self):
        initialize()
        self.player_turn = 1
        self.win = False
        self.tie = False
        self.restart_button.visible = False
        self.mainmenu_button.visible = False
        self.time = 0
        self.end_time = 0

    # Draw the grid based on values in the list
    def draw_grid(self):
        size = 100
        for row in range(ROWS):
            for col in range(COLUMNS):
                x = row * size + size
                y = col * size + size/2

                color = (0, 0, 0)
                if GRID[row*6 + col] == 1:
                    color = (255, 0, 0)
                elif GRID[row*6 + col] == 2:
                    color = (255, 220, 0)

                pygame.draw.circle(screen, color, (x, y), size/2 - 10, 0)

                # draws the green circle around winning tokens if game is won
                if GRID[row*6 + col] == "redwin":
                    pygame.draw.circle(screen, (255, 0, 0), (x, y), size/2 - 10, 0)
                    pygame.draw.circle(screen, (0, 255, 0), (x, y), size/2 - 10, 5)
                elif GRID[row*6 + col] == "yellowwin":
                    pygame.draw.circle(screen, (255, 220, 0), (x, y), size/2 - 10, 0)
                    pygame.draw.circle(screen, (0, 255, 0), (x, y), size/2 - 10, 5)

    # Checks for wins by checking 3 tokens in all directions and seeing if they are the same as the one that was placed.
    def check_for_win(self, placed_position):
        connections = {
            "Horizontal": [placed_position],
            "Vertical": [placed_position],
            "NorthEast": [placed_position],
            "NorthWest":[placed_position]
            }
                    
        for direction in [-1, 1, -5, 5, -6, 6, -7, 7]:
            for i in range(4):
                if placed_position + i * direction < len(GRID) and GRID[placed_position + i * direction] == self.player_turn:
                    
                    # Adds a token to the respected direction list
                    if i > 0:
                        if direction in [-6, 6]:
                            connections["Horizontal"].append(placed_position + i * direction)
                        elif direction in [-1, 1]:
                            connections["Vertical"].append(placed_position + i * direction)
                        elif direction in [-5, 5]:
                            connections["NorthEast"].append(placed_position + i * direction)
                        elif direction in [-7, 7]:
                            connections["NorthWest"].append(placed_position + i * direction)
                    
                    # Outputs a win if there are at least 3 consecutive tokens of the same type
                    for connection_count in connections.values():
                        if len(connection_count) >= 4:
                            for position in connection_count:
                                if self.player_turn == 1:
                                    GRID[position] = "redwin"
                                else:
                                    GRID[position] = "yellowwin"
                            return True

                    # Checks if the position is on an edge or corner, and stops it from checking further in that direction
                    if placed_position + i * direction in bottom_positions and direction in [1, -5, 7]:
                        break
                    if placed_position + i * direction in left_positions and direction in [-6, -5, -7]:
                        break
                    if placed_position + i * direction in right_positions and direction in [6, 5, 7]:
                        break
                    if placed_position + i * direction in top_positions and direction in [-1, 5, -7]:
                        break
                else:
                    break
    
    def draw(self):
        scene_manager.update()
        self.time += self.clock.tick(60) / 1000

        #Clears each surface
        screen.fill((30, 100, 255))
        circle_surface.fill((0, 0, 0, 0))

        self.draw_grid()

        floored_time = self.time // 1
        if self.end_time != 0:
            floored_time = self.end_time

        time_text = font.render(f"{int(floored_time // 60)}:{int(floored_time % 60):02d}", True, (255, 255, 255))

        current_turn_text = font.render("Current turn: Player " + player_colors[self.player_turn - 1], True, (255, 255, 255))
        if self.player_names[self.player_turn - 1] != "":
            current_turn_text = font.render("Current turn: " + self.player_names[self.player_turn - 1] + " (" + player_colors[self.player_turn - 1] + ")", True, (255, 255, 255))

        screen.blit(current_turn_text, (10, screen_height-50))
        screen.blit(time_text, (screen_width - time_text.get_width() - 10, screen_height-50))

        if self.win:
            if self.end_time == 0:
                self.end_time = floored_time

            # draw the win screen
            text_surface = font.render("Player " + player_colors[self.player_turn - 1] + " has won!", True, (255, 255, 255))
            if self.player_names[self.player_turn - 1] != "":
                text_surface = font.render(self.player_names[self.player_turn - 1] + " (" + player_colors[self.player_turn - 1] + ")" + " has won!", True, (255, 255, 255))
            
            screen.blit(text_surface, (screen_width/2 - text_surface.get_width()/2, screen_height/2 - 100))
            self.restart_button.draw()
            self.mainmenu_button.draw()
        elif self.tie:
            if self.end_time == 0:
                self.end_time = floored_time

            # draw the tie screen
            text_surface = font.render("Tie!", True, (255, 255, 255))
            screen.blit(text_surface, (screen_width/2 - text_surface.get_width()/2, screen_height/2 - 100))
            self.restart_button.draw()
            self.mainmenu_button.draw()
        else:
            # draw the game and run calculations
            mouse_pos = pygame.mouse.get_pos()

            # Snaps the token to the nearest column to the cursor
            previous_diff = None
            closest_column = None
            for x_pos in column_positions:
                if previous_diff != None:
                    if abs(x_pos - mouse_pos[0]) < previous_diff:
                        previous_diff = abs(x_pos - mouse_pos[0])
                        closest_column = x_pos
                    else:
                        break
                else:
                    previous_diff = abs(x_pos - mouse_pos[0])
                    closest_column = x_pos

            # Handles the placement location, finds the lowest row that is not occupied
            target_row = None
            self.target_grid = None
            for index in range(6):
                grid_value = GRID[column_positions.index(closest_column) * 6 + index]
                
                if grid_value > 0:
                    if index == 0:
                        break
                    target_row = row_positions[index - 1]
                    self.target_grid = column_positions.index(closest_column) * 6 + index - 1
                    break
                elif index == 5:
                    target_row = row_positions[index]
                    self.target_grid = column_positions.index(closest_column) * 6 + index

            # Draw the token hologram
            if target_row:
                pygame.draw.circle(circle_surface, hologram_colors[self.player_turn - 1], (closest_column, target_row), 40, 0)
                screen.blit(circle_surface, (0, 0))

    def handle_event(self, event):
        # Event handler
        if event.type == pygame.MOUSEBUTTONDOWN and not self.win and not self.tie:
            if event.button == 1:
                # Places the token
                if self.target_grid != None:
                    GRID[self.target_grid] = self.player_turn
                    token_place.play()

                    if self.check_for_win(self.target_grid):
                        self.win = True
                        win_sound.play()
                        return
                    
                    # Checks if there are no empty spots in the grid, if none then it is a tie.
                    fullgrid = True
                    for v in GRID:
                        if v == 0:
                            fullgrid = False
                    if fullgrid:
                        self.tie = True
                        return

                    # Swaps player turn
                    if self.player_turn == 1:
                        self.player_turn = 2
                    else:
                        self.player_turn = 1
        else:
            self.restart_button.handle_event(event)
            self.mainmenu_button.handle_event(event)

scene_manager.run(MainMenu())

pygame.quit()