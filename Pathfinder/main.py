from collections import deque
from queue import PriorityQueue
import pygame
import sys

#Pathfinding algorithms from CS50AI -0:Search

HEIGHT = 800
WIDTH = 800
CELL_SIZE = 20

WHITE = (255,255,255)
RED = (255, 0, 0) #start
GREEN = (0, 255, 0)
BLUE = (0, 0, 255) #end
GREY = (220, 220, 220) #lines
BLACK = (0, 0, 0) #wall
PINK = (255, 182, 193) #progression

class Node:
    
    def __init__(self, x, y, parent, color):
        self.x = x
        self.y = y
        self.parent = parent
        self.color = color
        
    def __lt__(self, other):
        return False
    
    def draw(self,win):
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        pygame.draw.rect(win, self.color, pygame.Rect(screen_x, screen_y,(screen_x + CELL_SIZE), (screen_y + CELL_SIZE)))
    
    def is_wall(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == RED
    
    def is_end(self):
        return self.color == BLUE
    
    def make_start(self):
        self.color = RED
    
    def make_end(self):
        self.color = BLUE
    
    def make_wall(self):
        self.color = BLACK
        
    def make_progress(self):
        self.color = PINK
    
    def make_path(self):
        self.color = BLUE
    
    def clear(self):
        self.color = WHITE
        
    def get_pos(self):
        return (self.x, self.y)
        
    

def get_neighbours(pos, grid):
    i,j = pos
    
    '''
    actions = [
        ('up', (i-1,j)),
        ('down', (i+1,j)),
        ('left', (i,j-1)),
        ('right', (i,j+1))
        ]
    '''
    actions = [(i-1,j), (i+1,j), (i,j-1), (i,j+1)]
    
    neighbours =[]
    for row, col in actions:
        if (0<=row<(HEIGHT//CELL_SIZE)) and (0<=col<(WIDTH//CELL_SIZE)) and (grid[row][col].is_wall() == False):
            neighbours.append((row,col))
    return neighbours
            
def make_grid():
    grid = []
    cells_per_row = WIDTH // CELL_SIZE
    cells_per_col = HEIGHT // CELL_SIZE
    for i in range(cells_per_col):
        grid.append([])
        for j in range(cells_per_row):
            n = Node(x=i, y = j, parent = None, color = WHITE)
            grid[i].append(n)
    return grid

def draw_grid(screen):
    for y in range(WIDTH//CELL_SIZE):
        pygame.draw.line(screen, GREY, (y*CELL_SIZE,0), (y*CELL_SIZE,HEIGHT))
    for x in range(HEIGHT//CELL_SIZE):
        pygame.draw.line(screen, GREY, (0,x*CELL_SIZE), (WIDTH, x*CELL_SIZE))
        
def draw(screen, grid):
    screen.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(screen)
    draw_grid(screen)
    pygame.display.update()

def get_clicked_pos(pos):
    y , x = pos
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    
    return row, col

#1 Depth first search: DFS
def DFS(source, target, screen, grid):
    '''
    Node source
    Node target
    HEIGHTxWIDTH array grid
    '''
    
    stack = [source]
    explored = set()
    
    while True:
        if not stack: #i.e stack empty and didn't find solution
            return None
        
        node = stack.pop()
        
        if node!=source and node != target:
            node.make_progress()
        position = node.get_pos()
        if position in explored:
            continue
        
        if position == target.get_pos():
            solution =[]
            while node.parent is not None:
                solution.append((node.x,node.y))
                node = node.parent
            solution.reverse()
            return solution
        
        for neighbour_pos in get_neighbours(position, grid):
            i,j = neighbour_pos
            tmp = Node(x=i,y=j, parent=node, color = WHITE)
            if (neighbour_pos not in explored) and (tmp not in stack):
                #turn neighbour into a child
                grid[i][j].parent = node
                stack.append(grid[i][j])
        
        explored.add(position)
        draw(screen,grid)

#2 Breadth first search
def BFS(source, target, screen, grid):
    '''
    Node source
    Node target
    HEIGHTxWIDTH array grid
    '''
    queue = deque([source])
    explored = set()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
                
        if not queue:
            return None
        
        node = queue.popleft()
        if node!=source and node != target:
            node.make_progress()
        position = node.get_pos()
        if position in explored:
            continue
        
        if position == target.get_pos():
            solution = []
            while node.parent is not None:
                solution.append(node.get_pos())
                node = node.parent
            solution.reverse()
            return solution
                
        for neighbour_pos in get_neighbours(position, grid):
            i,j = neighbour_pos
            tmp = Node(x=i,y=j, parent=node, color = WHITE)
            if (neighbour_pos not in explored) and  (tmp not in queue):
                grid[i][j].parent = node
                queue.append(grid[i][j])
        
        explored.add(position)
        draw(screen,grid)

def heuristic(pos1, pos2): #manhattan distance
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(y1 - y2) + abs(x1 - x2)

#3. Greedy Best Frist Search GBFS
def GBFS(source, target, screen, grid):
    pq = PriorityQueue()
    count = 0
    pq.put((0, count, source))
    pq_hash = {source.get_pos()}
    explored = set()
    
    while True:
        if pq.empty():
            return None
        
        node = pq.get()[2]
        if node!=source and node != target:
            node.make_progress()
        position = node.get_pos()
        pq_hash.remove(position)
        
        if position == target.get_pos():
            solution = []
            while node.parent is not None:
                solution.append(node.get_pos())
                node = node.parent
            solution.reverse()
            return solution
                
        for neighbour_pos in get_neighbours(position, grid):
            i, j = neighbour_pos
            if (neighbour_pos not in pq_hash) and (neighbour_pos not in explored):
                count +=1
                grid[i][j].parent = node
                pq.put((heuristic(target.get_pos(), neighbour_pos), count, grid[i][j]))
                pq_hash.add(neighbour_pos)
        
        explored.add(position)
        draw(screen,grid)
#4. A*
def AStar(source, target, screen, grid):
    pq = PriorityQueue()
    #items will be ordered based on the heuristic distance (h) of the node plus
    #cost of getting to the node (g_score)
    count = 0
    g_score = {node.get_pos():float("inf") for row in grid for node in row}
    g_score[source.get_pos()] = 0
    f_score = {node.get_pos():float("inf") for row in grid for node in row}
    f_score[source] = heuristic(source.get_pos(), target.get_pos())
    pq.put((0, count, source))
    pq_hash = {source.get_pos()} #keeps track of what's in the queue bc Priority Queue doesn't
    
    while True:
        if pq.empty():
            return None
        
        node = pq.get()[2]
        if node!=source and node != target:
            node.make_progress()
        position = node.get_pos()
        pq_hash.remove(position)
      
        if position == target.get_pos():
            solution = []
            while node.parent is not None:
                solution.append(node.get_pos())
                node = node.parent
            solution.reverse()
            return solution
                
        for neighbour_pos in get_neighbours(position, grid):
            i, j = neighbour_pos
            if neighbour_pos not in pq_hash:
                #check if the total cost using this path is lower than what we had
                temp_g_score = g_score[position] + 1
                if temp_g_score < g_score[neighbour_pos]:
                    count += 1
                    g_score[neighbour_pos] = temp_g_score
                    grid[i][j].parent = node
                    f_score[neighbour_pos] = temp_g_score +heuristic(target.get_pos(), neighbour_pos)
                    pq.put((f_score[neighbour_pos], count, grid[i][j]))
                    pq_hash.add(neighbour_pos)           
        
        draw(screen,grid)

def draw_answer_path(path, grid, screen):
    for node in path:
        i, j = node
        if grid[i][j].is_start() or grid[i][j].is_end():
            continue
        grid[i][j].color =GREEN
        draw(screen,grid)
           
def main():
    while True:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption('Pathfinder')
        
        mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
        largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
        
        img = pygame.image.load('kekw.jpg')
        img = pygame.transform.scale(img, (200,200))
        
        choice = None #which pathfinding algo does the user wanna see
    
        while not choice:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    
            screen.fill(PINK)
            
            title = largeFont.render("Select a pathfinding algorithm", True, WHITE)
            titleRect = title.get_rect()
            titleRect.center = ((WIDTH / 2), 50)
            screen.blit(title, titleRect)
            
            DFSButton = pygame.Rect((WIDTH / 12), (HEIGHT / 3), 320, 50)
            useDFS = mediumFont.render("Depth First Search", True, BLACK)
            DFSRect = useDFS.get_rect()
            DFSRect.center = DFSButton.center
            pygame.draw.rect(screen, WHITE, DFSButton)
            screen.blit(useDFS, DFSRect)
    
            BFSButton = pygame.Rect((6*(WIDTH / 12))+20, (HEIGHT / 3), 320, 50)
            useBFS = mediumFont.render("Breadth First Search", True, BLACK)
            BFSRect = useBFS.get_rect()
            BFSRect.center = BFSButton.center
            pygame.draw.rect(screen, WHITE, BFSButton)
            screen.blit(useBFS, BFSRect)
            
            GBFSButton = pygame.Rect(WIDTH / 12, (HEIGHT/2), 320, 50)
            useGBFS = mediumFont.render("Greedy Best First Search", True, BLACK)
            GBFSRect = useGBFS.get_rect()
            GBFSRect.center = GBFSButton.center
            pygame.draw.rect(screen, WHITE, GBFSButton)
            screen.blit(useGBFS, GBFSRect)
            
            ASButton = pygame.Rect((6*(WIDTH / 12))+20, (HEIGHT / 2), 320, 50)
            useAS = mediumFont.render("A* Search", True, BLACK)
            ASRect = useAS.get_rect()
            ASRect.center = ASButton.center
            pygame.draw.rect(screen, WHITE, ASButton)
            screen.blit(useAS, ASRect)
            
            click, _, _ = pygame.mouse.get_pressed()
            if click == 1:
                mouse = pygame.mouse.get_pos()
                if DFSButton.collidepoint(mouse):
                    choice = 'DFS'
                elif BFSButton.collidepoint(mouse):
                    choice = 'BFS'
                elif GBFSButton.collidepoint(mouse):
                    choice = 'GBFS'
                elif ASButton.collidepoint(mouse):
                    choice = 'AStar'
            pygame.display.update()
    
        grid = make_grid()
        new = True
        run = True
        started = False
        ns = False
        
        start = None
        end = None
        
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                    
                if started:
                    continue
                if pygame.mouse.get_pressed()[0]:
                    x, y = get_clicked_pos(pygame.mouse.get_pos())
                    node = grid[x][y]
                    if not start and node != end and new:
                        start = node
                        node.make_start()
                    
                    elif not end and node != start and new:
                        end = node
                        node.make_end()
                        
                    elif node!=start and node!=end and new:
                        node.make_wall()
                elif pygame.mouse.get_pressed()[2]:
                    if new == True:
                        x, y = get_clicked_pos(pygame.mouse.get_pos())
                        node = grid[x][y]
                        if node ==start:
                            start = None
                        elif node == end:
                            end = None
                        node.clear()
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and start and end:
                        started = True
                        new = False
                        
                    if event.key == pygame.K_c and not started:
                        start = None
                        end = None
                        grid = make_grid()
                        new = True
                        ns = False
                        draw(screen, grid)
                        
                    if event.key == pygame.K_ESCAPE and not started:
                        choice = None
                        run = False
            
            draw(screen,grid)
            
            if started:
                path = globals()[choice](start, end, screen, grid)
                if not path:
                    print('No solution')
                    ns = True
                    started = False
                else:
                    draw_answer_path(path, grid,screen)   
                    started = False
                    
            if ns:
                screen.blit(img, (WIDTH-200, 0))
                pygame.display.update()
                
if __name__ == '__main__':
    main()







