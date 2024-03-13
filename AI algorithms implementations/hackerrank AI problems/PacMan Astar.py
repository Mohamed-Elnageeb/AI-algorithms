# https://www.hackerrank.com/challenges/pacman-ucs 

from heapq import * 

def A_star(start,type = 1 , graph = [] , grid = [] , h = {} ) : 
    # initialize  the queue with starting node (distance = 0 , and no parent = -1 ) 
    queue = [(0 + h[start] , 0 ,start,-1)]   

    #  mark as visted
    vis[start[0]][start[1]] = True 

    # when dealing with a grid : (up , left , right , down transitions ) 
    # we can add diagonal transitions too 

    directions = [ (-1,0) , (0,-1) , (0,1), (1,0) ]


    # while queue is not empty 
    while queue : 
        
        # uncomment next line to see how the algorithm's queue works
        # print(queue)

        # pop the last node we pushed into the queue 
        cost , current_distance , current_node , parent = heappop(queue)


        # process the current node :
        process(current_node,parent)

        if current_node == goal : 
            printpath(goal) 
            break

        if type == 1 : 
            # 1 . if dealing iwth a graph add all adjacent nodes of current node to queue (except its parent)
            for child in graph[current_node] : 
                if child != parent : 
                    # new distance will be current distance + 1 and new parent will be current node
                    heappush (queue , ((current_distance + 1, child , current_node )) )

        else : 
            # 2. If dealing with a grid expand on all possible directions : 
            for dx,dy in directions : 
                i , j = current_node 
                newi = i + dx 
                newj = j + dy  
                # if current cell has a neighbor inside the grid boundaries in this direction add it to queue (if it is not blocked)
                if 0 <= newi < len(grid) and  0 <= newj < len(grid[0])  and vis[newi][newj] is False and grid[newi][newj] != "%" : 
                    vis[newi][newj] = True
                    heappush(queue,  (current_distance + h[newi,newj] + 1 , current_distance + 1 , (newi,newj) , (i,j)) )



def process(node,par) : 
    # do something 
    parent_map[node] = par
    # print(node[0]+1,node[1] + 1) 


def printpath(goal) : 
    path = [goal]
    current = goal 
    while current != start : 
        current = parent_map[current] 
        path.append(current) 
    path.reverse() 
    
    print(len(path)-1)
    for node in path :
        print(node[0] , node[1] )


start = tuple(map(int,input().split())) 
goal = tuple(map(int,input().split()))  
n,m = tuple(map(int,input().split()))  


parent_map = {}

grid = [] 
for _ in range(n) : 
    grid.append(input())

h = {} 
for i in range(n) : 
    for j in range(m) : 
        h[i,j] = abs(i - goal[0]) + abs(j - goal[1]) 
        
# run dfs algorithm and keep track of visted nodes in order to avoid loops 
vis = [[False for i in range(m) ] for j in range(n)]
A_star(start , 2 , grid = grid , h = h)