def rabin_karp(text,pattren):
    n=len(text)
    m=len(pattren)
    if n<m:
        return []
    prime=101
    pattren_hash=0
    text_hash=0
    for i in range(m):
        pattren_hash=(pattren_hash*256+ord(pattren[i]))%prime
        text_hash=(text_hash*256+ord(text[i]))%prime
    matches=[]
    for i in range(n-m+1):
        if pattren_hash==text_hash and text[i:i+m]==pattren:
            matches.append(i)
        if i<n-m:
            text_hash=(256*(text_hash-ord(text[i])*pow(256,m-1,prime))+ord(text[i+m]))%prime
    return matches
text=input("enter the text: ")
pattren=input("enter the pattren to search:")
matches=rabin_karp(text,pattren)
if matches:
    print("pattren found at index: ",matches)
else:
    print("pattren not found in the text")
    
    
    