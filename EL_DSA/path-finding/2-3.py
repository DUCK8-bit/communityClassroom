class TreeNode:
    def __init__(self,is_leaf=True):
        self.keys=[]
        self.children=[]
        self.is_leaf=is_leaf
    def split_child(self,i,child):
        new_child=TreeNode(is_leaf=child.is_leaf)
        self.children.insert(i+1,new_child)
        self.keys.insert(i,child.keys.pop())
        new_child.keys=child.keys[len(child.keys)//2:]
        child.keys=child.keys[:len(child.keys)//2]
        if not child.is_leaf:
            new_child.children=child.children[len(child.children)//2:]
            child.children=child.children[:len(child.children)//2]
    def insert_non_full(self,key):
        i=len(self.keys)-1
        if self.is_leaf:
            self.keys.append(None)
            while i>=0 and key<self.keys[i]:
                self.keys[i+1]=self.keys[i]
                i-=1
            self.keys[i+1]=key
        else:
            while i>=0 and key<self.keys[i]:
                i-=1
            i+=1
            if(len(self.children[i].keys))==2:
                self.split_child(i,self.children[i])
                if key>self.keys[i]:
                    i+=1
                self.children[i].insert_non_full(key)
    def search(self,key):
        i=0
        while i<len(self.keys) and key>self.keys[i]:
            i+=1
        if i<len(self.keys)and key==self.keys[i]:
            return True
        elif self.is_leaf:
            return False
        else:
            return self.children[i].search(key)
class Tree234:
    def __init__(self):
        self.root=TreeNode()
    def insert(self,key):
        if len(self.root.keys)==3:
            new_root=TreeNode(is_leaf=False)
            new_root.children.append(self.root)
            new_root.split_child(0,self.root)
            self.root=new_root
        self.root.insert_non_full(key)
    def search(self,key):
        return self.root.search(key)
        
def main():
    tree=Tree234()
    print("enter keys to insert :")
    keys=input().split()
    for key in keys:
        try:
            key=int(key)
            tree.insert(key)
            print(f"key{key}inserted sucessfully")
        except ValueError:
            print(f"invalid input'{key}. please enter an integer key")
    print("\n enter key to be searched")
    search_key=input()
    try:
        search_key=int(search_key)
        if tree.search(search_key):
            print(f"key {search_key} found in tree")
        else:
            print(f"key {search_key} not found in tree")
    except ValueError:
        print("invalid input. PLease enter an integer key")
if __name__=="__main__":
    main()
        
                
        