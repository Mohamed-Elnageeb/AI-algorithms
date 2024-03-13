from collections import deque  # double ended queue that supports popping from the left in o(1) 

def BFS(start,type = 1 , graph = [] , grid = [] ) : 
    # initialize  the queue with starting node (distance = 0 , node = starting i and j , and no parent = -1 ) 
    queue = deque([(0,start,-1)] )
    
    # when dealing with a grid (up ,down, left , right transitions ) 
    # we can add diagonal transitions too 

    directions = [ (-1,0) , (1,0) , (0,-1) , (0,1)]

    # while queue is not empty 
    while queue : 
        # uncomment next line to see how the algorithm's queue works
        # see_queue(queue)

        # pop the earliest node we pushed into the current queue 
        current_distance , current_node , parent = queue.popleft() 

        # process the current node :
        process(current_node,parent)

        if current_node == goal : 
            printpath(goal,current_distance) 
            break

        if type == 1 : 
            # 1 . if dealing iwth a graph add all adjacent nodes of current node to queue (except its parent , or those visted if using closed list )
            for child , weight in graph[current_node] : 
                if child != parent : 
                    # new distance will be current distance + weight and new parent will be current node
                    queue.append((current_distance + weight, child , current_node ))

        else : 
            # 2. If dealing with a grid expand on all possible directions : 
            for dx,dy in directions : 
                i , j = current_node 
                newi = i + dx 
                newj = j + dy  
                # if current cell has a neighbor inside the grid boundaries in this direction add it to queue 
                if 0 <= newi <= len(grid) and  0 <= newj <= len(grid[0])  and (newi,newj) != parent: 
                    queue.append( (current_distance + 1 , (newi,newj) , (i,j)) )


def process(node,par) : 
    # do something 
    parent_map[node] = par
    # print(*node) 


def see_queue(q) : 
    cur = [] 
    for i in reversed(range(len(q))) : 
        cur.append(q[i])
    cur.reverse()
    print("current queue :",cur) 
    print("next node expanded ----->", cur[0])
    print()

def printpath(goal,cost) : 
    path = [goal]
    current = goal 
    while current != -1 : 
        current = parent_map[current] 
        path.append(current) 
    path.reverse() 
    
    print("number of moves : ", len(path)-1)
    for move in path[1:] :
        if move == goal : 
            print(move)
        else:
            print(move,end= " -> ") 
    print("cost :",cost)
# sample usage on a graph (see q1.jpg ) 
    
# initiating adjacency list as a dictionary :
graph = {"S" : [ ("A",2),("F",3),("B",1)] , 
     "B" : [ ("D",2),("E",4)] ,
     "A" : [ ("C",2),("D",3)] ,
     "F" : [ ("G",6) ] ,
     "C" : [ ("G",4) ] ,
     "D" : [ ("G",4) ] ,
     "G" : [] ,
     "E" :  []
       }
#initiate heuristic function values as a dictionary : 
heuristic_function =  {"S" : 6 , 
     "B" : 5 ,
     "A" : 4 ,
     "F" : 4 ,
     "C" : 2 ,
     "D" : 2 ,
     "G" : 0 ,
     "E" :  8
       }

goal = "G"
parent_map = {} 

#run BFS algorithm on the graph (for graphs with loops use a closed list to avoid visting nodes twice) :  
BFS( "S" , type= 1 , graph=graph)




# sample usage problem : https://www.hackerrank.com/challenges/pacman-bfs