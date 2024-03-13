from heapq import *  # heapq data structure allows us to store queue ordered by cost and pop the least node in o(logn)

def UCS(start,type = 1 , graph = [] , grid = [] ) : 
    # initialize  the queue with starting node (distance = 0 , and no parent = -1 ) 
    queue = [(0,start,-1)]   

    #  mark as visted
    # vis[start[0]][start[1]] = True 

    # when dealing with a grid : (up , left , right , down transitions ) 
    # we can add diagonal transitions too 

    directions = [ (-1,0) , (0,-1) , (0,1), (1,0) ]


    # while queue is not empty 
    while queue : 
        
        # uncomment next line to see how the algorithm's queue works
        see_queue(queue)

        # pop the last node with the least distance from starting node (if there is a tie break it with alphabetical ordering)
        current_distance , current_node , parent = heappop(queue)


        # process the current node :
        process(current_node,parent)

        if current_node == goal : 
            printpath(goal,current_distance) 
            break

        if type == 1 : 
            # 1 . if dealing iwth a graph add all adjacent nodes of current node to queue (except its parent)
            for child,weight in sorted(graph[current_node]) : 
                # add children in alphabetical order while adding corresponding edge weight 
                if child != parent : 
                    # new distance will be current distance + edge weight and new parent will be current node
                    heappush(queue,((current_distance + weight , child , current_node )))

        else : 
            # 2. If dealing with a grid expand on all possible directions : 
            for dx,dy in directions : 
                i , j = current_node 
                newi = i + dx 
                newj = j + dy  
                # if current cell has a neighbor inside the grid boundaries in this direction add it to queue (if it is not blocked)
                if 0 <= newi < len(grid) and  0 <= newj < len(grid[0])  and vis[newi][newj] is False and grid[newi][newj] != "%" : 
                    # vis[newi][newj] = True
                    heappush(queue,  (current_distance + 1 , (newi,newj) , (i,j)) )


def see_queue(q) : 
    cur = [] 
    q_copy = q.copy() 
    for i in reversed(range(len(q_copy))) : 
        cur.append(heappop(q_copy))
    print("current queue :",cur) 
    print("next node expanded ----->", cur[0])
    print()

def process(node,par) : 
    # do something 
    parent_map[node] = par
    # print(*node) 


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

#run UCS algorithm on the graph : 
UCS( "S" , type= 1 , graph=graph)


# sample usage problem : https://www.hackerrank.com/challenges/pacman-ucs 

