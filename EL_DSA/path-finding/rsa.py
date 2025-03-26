def pow(base,expo,m):
    res=1
    base=base%m
    while expo>0:
        if expo & 1:
            res=(res*base)%m
        base=(base*base)%m
        expo=expo//2
    return res
def modinverse(e,phi):
    for d in range(2,phi):
        if(e*d)%phi==1:
            return d
    return -1
def generatekeys():
    p=7919
    q=1009
    n=p*q
    phi=(p-1)*(q-1)
    e=0
    for e in range(2,phi):
        if(gcd(e,phi))==1:
            break
    d=modinverse(e,phi)
    return e,d,n
def gcd(a,b):
    while b!=0:
        a,b=b,a%b
    return a
def encrypt(m,e,n):
    return pow(m,e,n)
def decrypt(c,d,n):
    return pow(c,d,n)
if __name__=="__main__":
    e,d,n=generatekeys()
    print(f"public key (e,n):({e},{n}) ")
    print(f"private key (d,n):({d},{n})")
    m=int(input("enter the message: "))
    print(f"original message :{m}")
    c=encrypt(m,e,n)
    print(f"encrypted message :{c}")
    d=decrypt(c,d,n)
    print(f"decrypted message:{d}")
    

    
            
        