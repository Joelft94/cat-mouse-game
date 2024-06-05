import pygame
import random
import sys
import time

pygame.mixer.init()

# Tamaño de la cuadrícula
GRID_SIZE = 5
CELL_SIZE = 80
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT_SIZE = 36
MAX_DEPTH = 5


# Load sound files
mouse_win_sound = pygame.mixer.Sound("./sounds/scream.mp3")
cat_win_sound = pygame.mixer.Sound("./sounds/lose.mp3")
    
    
# Direcciones para arriba, abajo, izquierda, derecha
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Función para dibujar la cuadrícula
def draw_grid(screen):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

# Función para verificar si dos posiciones son adyacentes
def is_adjacent(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

# Función para inicializar las posiciones
def initialize_positions():
    global cat_pos, mouse_pos, hole_pos


    # El gato empieza en la primera celda
    cat_pos = (0, 0)

    # El ratón empieza en la última celda de la cuadrícula
    mouse_pos = (GRID_SIZE - 1, GRID_SIZE - 1)

    # Inicializar la posición del agujero asegurando que no esté en las posiciones iniciales del gato o el ratón
    # hole_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    # Esto si queremos que sea random el agujero
    
    # Con esto el agujero inicia en un lugar random entre la primera y segunda fila
    hole_pos = ((random.randint(0,1)) , random.randint(0, GRID_SIZE - 1))
    while hole_pos == cat_pos or hole_pos == mouse_pos:
        hole_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

# Función para obtener los movimientos posibles
def get_possible_moves(position, is_cat_turn):
    moves = []
    for d in DIRECTIONS:
        new_pos = (position[0] + d[0], position[1] + d[1])
        if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE:
            if is_cat_turn and new_pos == hole_pos:
                continue  # Skip the hole if it's the cat's turn
            moves.append(new_pos)
    return moves

# Función para mostrar al ganador
def display_winner(screen, winner):
    font = pygame.font.SysFont(None, FONT_SIZE)
    text = font.render(f"{winner} wins!", True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
    screen.blit(text, text_rect)

# Función para evaluar la posición actual
def evaluate(cat_pos, mouse_pos, hole_pos):
    if mouse_pos == hole_pos:
        return -1000  # Gana el ratón
    if cat_pos == mouse_pos:
        return 1000  # Gana el gato

    # Distancias
    mouse_to_hole = abs(mouse_pos[0] - hole_pos[0]) + abs(mouse_pos[1] - hole_pos[1])
    cat_to_mouse = abs(cat_pos[0] - mouse_pos[0]) + abs(cat_pos[1] - mouse_pos[1])
    cat_to_hole = abs(cat_pos[0] - hole_pos[0]) + abs(cat_pos[1] - hole_pos[1])

    # Evaluar la posición actual
    return 10 * (mouse_to_hole - cat_to_mouse) + cat_to_hole  # Motivar al gato a acercarse al ratón y proteger el agujero

# Función para el algoritmo minimax
def minimax(cat_pos, mouse_pos, hole_pos, depth, is_cat_turn):
    if depth == 0 or cat_pos == mouse_pos or mouse_pos == hole_pos:
        return evaluate(cat_pos, mouse_pos, hole_pos)

    if is_cat_turn:
        max_eval = -float('inf') # Inicia con infinito negativo ya que cualquier valor mayor a eso va a tomar su lugar en la variable mas abajo
        for move in get_possible_moves(cat_pos, is_cat_turn):
            eval = minimax(move, mouse_pos, hole_pos, depth - 1, False)
            max_eval = max(max_eval, eval) # Se toma el valor máximo entre el valor actual y el valor de la evaluación para la variable
        return max_eval
    else:
        min_eval = float('inf') # Inicia con infinito positivo ya que cualquier valor menor a eso va a tomar su lugar en la variable mas abajo
        for move in get_possible_moves(mouse_pos, is_cat_turn):
            eval = minimax(cat_pos, move, hole_pos, depth - 1, True)
            min_eval = min(min_eval, eval) # Se toma el valor mínimo entre el valor actual y el valor de la evaluación para la variable
        return min_eval

# Función para obtener el mejor movimiento
def best_move(position, hole_pos, is_cat_turn):
    best_move = None
    if is_cat_turn:
        max_eval = -float('inf')
        for move in get_possible_moves(position, is_cat_turn):
            eval = minimax(move, mouse_pos, hole_pos, MAX_DEPTH - 1, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            elif eval == max_eval and random.random() < 0.5:
                # Agregamos random para que el gato no siempre tome el mismo camino si hay varias opciones con la misma evaluación
                best_move = move
    else:
        min_eval = float('inf')
        for move in get_possible_moves(position, is_cat_turn):
            if move == hole_pos:
                return move  # Immediately move to the hole if possible
            eval = minimax(cat_pos, move, hole_pos, MAX_DEPTH - 1, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
    return best_move



# Función principal
def main():
    global cat_pos, mouse_pos, hole_pos
    counter = 0

    # Initialize Pygame
    pygame.init()

    # Inicializar las posiciones
    initialize_positions()


    # Cargar las imágenes de los sprites y redimensionarlas para que quepan en una celda de la cuadrícula
    cat_image = pygame.transform.scale(pygame.image.load("./static/tom.jpg"), (CELL_SIZE, CELL_SIZE))
    mouse_image = pygame.transform.scale(pygame.image.load("./static/jerry.png"), (CELL_SIZE, CELL_SIZE))
    hole_image = pygame.transform.scale(pygame.image.load("./static/hole.png"), (CELL_SIZE, CELL_SIZE))

    

    # Definimos las propiedades de la ventana
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Cat and Mouse")

    clock = pygame.time.Clock()  # Initialize the clock

    is_cat_turn = True  # Initialize with cat's turn
    game_over = False  # Initialize game over flag

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        screen.fill(BLACK)

        # Draw grid lines
        draw_grid(screen)

        
        # Dibuja el sprite del gato
        cat_rect = cat_image.get_rect()
        cat_rect.topleft = (cat_pos[1] * CELL_SIZE, cat_pos[0] * CELL_SIZE)
        screen.blit(cat_image, cat_rect)

    
        # Dibuja el sprite del ratón
        mouse_rect = mouse_image.get_rect()
        mouse_rect.topleft = (mouse_pos[1] * CELL_SIZE, mouse_pos[0] * CELL_SIZE)
        screen.blit(mouse_image, mouse_rect)

        # Dibuja el sprite del agujero
        hole_rect = hole_image.get_rect()
        hole_rect.topleft = (hole_pos[1] * CELL_SIZE, hole_pos[0] * CELL_SIZE)
        screen.blit(hole_image, hole_rect)

        pygame.display.flip()

        if is_cat_turn:
            if counter ==  10:
                # Si llega a 10 turnos gana el gato
                winner = "Cat"
                game_over = True
                cat_win_sound.play()
            # Turno del gato
            cat_move = best_move(cat_pos, hole_pos, is_cat_turn=True)
            # Actualizar la posición del gato
            cat_pos = cat_move if cat_move is not None else cat_pos

            # Verificar las condiciones de victoria después del turno del gato
            if cat_pos == mouse_pos:
                winner = "Cat"
                game_over = True
                cat_win_sound.play()
        else:
            # Turno del ratón
            mouse_move = best_move(mouse_pos, hole_pos, is_cat_turn=False)
            # Actualizar la posición del ratón
            mouse_pos = mouse_move if mouse_move is not None else mouse_pos
            counter = counter + 1

            # Verificar las condiciones de victoria después del turno del ratón
            if mouse_pos == hole_pos:
                winner = "Mouse"
                game_over = True
                mouse_win_sound.play()

        is_cat_turn = not is_cat_turn  # Alternate turns

        clock.tick(1)  # Limita a 1 frame por segundo

    display_winner(screen, winner)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()





if __name__ == "__main__":
    main()


