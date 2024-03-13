# https://www.hackerrank.com/challenges/n-puzzle/problem

from heapq import * 


def h(state,final) : 
    cost = 0 
    
    for i in range(k) :
        for j in range(k) :
            val = state[i][j]
            if val != final[i][j] : 
                cost += 2
            cost += abs(i-place[val][0]) + abs(j-place[val][1])
    return cost  

def s(state) :
    arr =[] 
    for row in state : 
        arr.extend(row)  
    tup = tuple(arr) 
    return tup 

def A_star(start , grid   ) : 
    # initialize  the queue with starting node (distance = 0 , and no parent = -1 ) 

    for i in range(k) : 
        for j in range(k) : 
            if start[i][j] == 0 : 
                si,sj = i,j 
                break

    queue = [( h(start,final)  , (si,sj) , start , "" )]   
    #  mark as visted
    vis.add(s(start))

    # when dealing with a grid : (up , left , right , down transitions ) 
    # we can add diagonal transitions too 

    directions = [ (-1,0) , (0,-1) , (0,1), (1,0) ]
    name = ["UP","LEFT","RIGHT","DOWN"]

    parent_map[s(start)] = -1

    # while queue is not empty 
    while queue : 
        
        # uncomment next line to see how the algorithm's queue works
        # see_queue(queue)

        # pop the last node we pushed into the queue 
        cost  , current_node , state , prev_move  = heappop(queue)

        tup1 = s(state)

        if cost == 0 : 
            printpath((tup1 , prev_move)) 
            break
        
        idx = -1
        for dx,dy in directions : 
            idx += 1
            i , j = current_node 
            newi = i + dx 
            newj = j + dy  
            if 0 <= newi < len(grid) and  0 <= newj < len(grid[0]) :
                new_state = [row.copy() for row in state] 
                new_state[i][j] , new_state[newi][newj] = new_state[newi][newj] , new_state[i][j]
                tup2 = s(new_state)
            else:
                continue
            # if current cell has a neighbor inside the grid boundaries in this direction add it to queue (if it is not blocked)
            if 0 <= newi < len(grid) and  0 <= newj < len(grid[0])  and tup2 not in vis :  
                vis.add(tup2)
                parent_map[(tup2 , name[idx])] = (tup1 , prev_move)
                heappush(queue,  (  h(new_state,final)   , (newi,newj) , new_state , name[idx] ) )


def see_queue(q) : 
    cur = [] 
    q_copy = q.copy() 
    for i in reversed(range(len(q_copy))) : 
        cur.append(heappop(q_copy))
    print("current queue :",cur) 
    print("next node expanded ----->", cur[0])
    print() 

def printpath(goal) : 
    path = [goal[1]]
    current = goal 
    while current[0] != s(start) : 
        current = parent_map[current] 
        path.append(current[1]) 
    path.reverse() 
    
    print(len(path)-1)
    for move in path[1:] :
        print(move) 


parent_map = {}
k = int(input())
grid = [[] for _ in range(k)] 
for i in range(k) : 
    for j in range(k) : 
        grid[i].append(int(input()) ) 

start = grid.copy()   
final = [[] for _ in range(k)] 
nxt = 0 
for i in range(k) : 
    for j in range(k) : 
        final[i].append(nxt) 
        nxt += 1
place = {} 
for i in range(k) :
    for j in range(k) :
        place[final[i][j]] = (i,j)
# run dfs algorithm and keep track of visted nodes in order to avoid loops 
vis = set() 
A_star(start ,  grid )