# https://www.hackerrank.com/challenges/pacman-dfs 

def DFS(start,type = 1 , graph = [] , grid = [] ) : 
    # initialize  the queue with starting node (distance = 0 , node = starting i and j , and no parent = -1 ) 
    queue = [(0,start,-1)]   

    #  mark as visted
    vis[start[0]][start[1]] = True 

    # when dealing with a grid (up , left , right , down transitions ) 
    # we can add diagonal transitions too 

    directions = [ (-1,0) , (0,-1) , (0,1), (1,0) ]

    explored = [] 

    # while queue is not empty 
    while queue : 
        
        # uncomment next line to see how the algorithm's queue works
        # see_queue(queue)

        # pop the last node we pushed into the queue 
        current_distance , current_node , parent = queue.pop() 


        # process the current node :
        process(current_node,parent)
        explored.append(current_node)

        if current_node == goal : 
            print(len(explored)) 
            for node in explored : 
                print(*node)
            printpath(goal) 
            break

        if type == 1 : 
            # 1 . if dealing iwth a graph add all adjacent nodes of current node to queue (except its parent)
            for child in graph[current_node] : 
                if child != parent : 
                    # new distance will be current distance + 1 and new parent will be current node
                    queue.append((current_distance + 1, child , current_node ))

        else : 
            # 2. If dealing with a grid expand on all possible directions : 
            for dx,dy in directions : 
                i , j = current_node 
                newi = i + dx 
                newj = j + dy  
                # if current cell has a neighbor inside the grid boundaries in this direction add it to queue (if it is not blocked)
                if 0 <= newi < len(grid) and  0 <= newj < len(grid[0])  and vis[newi][newj] is False and grid[newi][newj] != "%" : 
                    vis[newi][newj] = True
                    queue.append( (current_distance + 1 , (newi,newj) , (i,j)) )



def process(node,par) : 
    # do something 
    parent_map[node] = par
    # print(node[0]+1,node[1] + 1) 

def see_queue(q) : 
    cur = [] 
    for i in reversed(range(len(q))) : 
        cur.append(q[i])
    print("current queue :",cur) 
    print("next node expanded ----->", cur[0])

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

# run dfs algorithm and keep track of visted nodes in order to avoid loops 
vis = [[False for i in range(m) ] for j in range(n)]
DFS(start , 2 , grid = grid)