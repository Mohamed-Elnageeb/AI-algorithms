from collections import deque  # double ended queue that supports popping from the left in o(1) 

def BFS(start,type = 1 , graph = [] , grid = [] ) : 
    # initialize  the queue with starting node (distance = 0 , and no parent = -1 ) 
    queue = deque([(0,start,-1)] )
    
    # when dealing with a grid (up ,down, left , right transitions ) 
    # we can add diagonal transitions too 

    directions = [ (-1,0) , (1,0) , (0,-1) , (0,1)]

    # while queue is not empty 
    while queue : 
        
        # uncomment next line to see how the algorithm's queue works
        # print(queue)

        # pop the last node we pushed into the queue 
        current_distance , current_node , parent = queue.pop() 

        # process the current node :
        process(current_node)

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
                # if current cell has a neighbor inside the grid boundaries in this direction add it to queue 
                if 0 <= newi <= len(grid) and  0<= newj <= len(grid[0])  and (newi,newj) != parent: 
                    queue.append( (current_distance + 1 , (newi,newj) , (i,j)) )



def process(node) : 
    # do something 
    print(node) 




# example usage on a grid 
    





# sample usage problem : https://www.hackerrank.com/challenges/pacman-bfs