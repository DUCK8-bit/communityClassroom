import sys
def matrix_chain_order(p):
    n=len(p)-1
    m=[[0]*(n+1) for _ in range(n+1)]
    s=[[0]*(n+1) for _ in range(n+1)]
    for l in range(2,n+1):
        for i in range(1,n-l+2):
            j=i+l-1
            m[i][j]=sys.maxsize
            for k in range(i,j):
                q=m[i][k]+m[k+1][j]+p[i-1]*p[i-1]*p[k]*p[j]
                if q<m[i][j]:
                    m[i][j]=q
                    s[i][j]=k
    return m,s
def print_optimal_parens(s,i,j):
    if i==j:
        print("A"+str(i),end="")
    else:
        print("(",end="")
        print_optimal_parens(s,i,s[i][j])
        print_optimal_parens(s,s[i][j]+1,j)
        print(")",end="")
def take_input():
    n=int(input("enter the number of matrices: "))
    dimesions=[]
    for i in range(n):
        dim=int(input(f"enter the dimensions of matrix {i+1}: "))
        dimesions.append(dim)
    return dimesions
matrix_sizes=take_input()
m,s=matrix_chain_order(matrix_sizes)
print("minimum number of matrix chain multiplications required ",m[1][len(matrix_sizes)-1])
print("optimal parenthesis:",end="")
print_optimal_parens(s,1,len(matrix_sizes)-1)
        