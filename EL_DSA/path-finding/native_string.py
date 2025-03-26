def native_string_matching(text,pattren):
    n=len(text)
    m=len(pattren)
    matches=[]
    for i in range(n-m+1):
        j=0
        while j< m and text[i+j]==pattren[j]:
            j+=1
        if j==m:
            matches.append(i)
    return matches
text=input("enter the text :")
pattren =input("enter the pattren to search :")
matches=native_string_matching(text,pattren)
if matches:
    print("pattren found at index :",matches)
else:
    print("pattren not found in text.")