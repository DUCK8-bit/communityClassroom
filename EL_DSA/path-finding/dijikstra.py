import heapq
class Graph:
    def __init__(self,vertices):
        self.V=vertices
        self.graph=[[]for _ in range(vertices)]
    def add_edge(self,u,v,w):
        self.graph[u].append((v,w))
        self.graph[v].append((u,w))
    def dijkstra(self,src):
        dist=[float('inf')]*self.V
        dist[src]=0
        visited=[False]*self.V
        pq=[(0,src)]
        while pq:
            d,u=heapq.heappop(pq)
            visited[u]=True
            for v,w in self.graph[u]:
                if not visited[v] and dist[u]+w<dist[v]:
                    dist[v]=dist[u]+w
                    heapq.heappush(pq,(dist[v],v))
        print("vertex \t distance from source")
        for i in range(self.V):
            print(i,"\t",dist[i])
V=int(input("enter the number of vertices: "))
g=Graph(V)
E=int(input("enter the number of edges: "))
print("enter the edgess with their weights (u v w):")
for _ in range(E):
    u,v,w=map(int,input().split())
    g.add_edge(u,v,w)
src =int(input("enter the source vertex: "))
g.dijkstra(src)    
