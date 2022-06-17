
import sys
import pickle
import csv
import math

#index file에 저장하는 정보
#트리의 degree, 리프 노드의 key와 value 값저장함
class saving:
    def __init__(self, degree):
        self.degree = degree
        self.pair = {} # {key : value} 형태의 딕셔너리

    def AddPair(self, pair):
        self.pair = pair

    def ClearPair(self):
        self.pair.clear()

    #주어진 정보로 트리를 구성하는 함수
    def createTree(self):
        bpt = BPTree(self.degree)
        key = list(self.pair.keys())
        value = list(self.pair.values())
        for i in range(len(key)):
            bpt.insert(key[i], value[i])
        return bpt


class Non_Leaf:
    def __init__(self):
        self.cnt_key = 0
        self.pair = {} #<key, left_child_node> pair, 딕셔너리 사용
        self.key_list=[]
        self.right_node = None #가장 오른쪽에 있는 child node의 ptr
        self.leaf = False
        self.parent = None #부모 노드를 가리키는 변수
    
    def split(self):
        Right = Non_Leaf()
        top = Non_Leaf()

        mid = math.floor(self.cnt_key/2) #나누는 기준 mid는 key의 개수의 반이다. 나누기 2한 값에 내림해서 구함 (왜냐하면 인덱스 값이기 때문에)

        #Right Node의 데이터 정리
        Right.key_list = self.key_list[mid+1:]
        for i in range(mid+1, self.cnt_key):
            temp ={}
            temp[self.key_list[i]] = self.pair[self.key_list[i]]
            Right.pair.update(temp)
            #키 순서에 맞게 재정렬
            Right.pair = sorted(Right.pair.items(), key = lambda t : t[0])
            Right.pair = dict(Right.pair)
            Right.cnt_key +=1

        Right.right_node = self.right_node

        Left = self
        temp_pair = self.pair
        temp_key_list = self.key_list
        Left.cnt_key = 0
        Left.pair = {}
        Left.key_list = []
        Left.leaf = False

        #Left Node의 데이터 정리
        Left.key_list = temp_key_list[:mid]
        for i in range(mid):
            temp ={}
            temp[temp_key_list[i]] = temp_pair[temp_key_list[i]]
            Left.pair.update(temp)
            #키 순서에 맞게 재정렬
            Left.pair = sorted(Left.pair.items(), key = lambda t : t[0])
            Left.pair = dict(Left.pair)
            Left.cnt_key +=1

        Left.right_node = temp_pair[temp_key_list[mid]]

        #밑에 자식노드의 부모 노드 재설정해야함
        for i in range(Left.cnt_key):
            Left.pair[Left.key_list[i]].parent = Left
        Left.right_node.parent = Left
        for i in range(Right.cnt_key):
            Right.pair[Right.key_list[i]].parent = Right
        Right.right_node.parent = Right

        #부모 노드로 올라간 mid의 키 값을 가진 top노드
        top.cnt_key+=1
        top.pair = {temp_key_list[mid]: Left}
        top.key_list = [temp_key_list[mid]]
        top.right_node = Right

        #Left와 Right 부모 노드와 연결
        Left.parent = top
        Right.parent = top

        return top

    def Add_NonLeaf(self, key, left_child):
        for i in range(self.cnt_key):
            if (key < self.key_list[i]):
                temp = {}
                temp[key] = left_child
                self.pair.update(temp)
                self.pair = sorted(self.pair.items(), key = lambda t : t[0])
                self.pair = dict(self.pair)
                self.cnt_key +=1
                self.key_list.append(key)
                self.key_list.sort()
                return
            #삽입하려는 키가 노드의 key_list에 있는 키들보다 큰 경우
            elif (key >= self.key_list[i] and i == self.cnt_key-1):
                temp = {}
                temp[key] = self.right_node
                self.pair.update(temp)
                self.pair = sorted(self.pair.items(), key = lambda t : t[0])
                self.pair = dict(self.pair)
                self.cnt_key +=1
                self.key_list.append(key)
                self.key_list.sort()
                self.right_node = left_child
                return
        
    def change(self, ex_key, new_key): #ex_key를 new_key로 바꿀경우 (그 외의 것 안바꿈)
        for i in range(self.cnt_key):
            #ex_key가 key_list에 존재하면 for문을 탈출, 1을 반환
            if (self.key_list[i] == ex_key):
                break
            #ex_key가 key_list에 존재하지 않으면 -1을 반환
            elif(self.key_list[i] != ex_key and i+1 == self.cnt_key):
                return -1
        self.pair[new_key] = self.pair.pop(ex_key)
        self.key_list.remove(ex_key)
        self.key_list.append(new_key)
        self.key_list.sort()
        return 1

    def Delete_NonLeaf(self, del_key): #del_key를 부모노드의 key_list에서 삭제하는경우
        #키가 하나일때
        if (self.cnt_key==1):
            self.cnt_key-=1
            self.pair = {}
            self.key_list = []
            return

        #가장 처음에 있는 노드에 있는 키 값을 삭제할 때
        if (self.key_list[0] > del_key):
            #자식노드가 리프노드일때 prev_node, right_node 다시 연결
            if (self.pair[self.key_list[0]].leaf == True):
                child = self.pair[self.key_list[0]]
                child.right_node.prev_node = child.prev_node
                #완전 맨처음 노드가 아닐경우에만
                if (child.prev_node != None):
                    child.prev_node.right_node = child.right_node 
            del self.pair[self.key_list[0]]
            del self.key_list[0]
            self.cnt_key-=1
            return 
        else:
            for i in range(self.cnt_key):
                if (self.key_list[i] > del_key):
                    #자식노드가 리프노드이면 prev_node, right_node 다시 연결
                    if (self.pair[self.key_list[i]].leaf == True):
                        tmp = self.pair[self.key_list[i]]
                        tmp.prev_node.right_node = tmp.right_node
                        tmp.right_node.prev_node = tmp.prev_node
                    del self.pair[self.key_list[i]]
                    del self.key_list[i]
                    self.cnt_key-=1
                    return

                #만일 지우려고 하는 노드가 가장 오른쪽에 있는 노드일때
                #맨 마지막 pair와 키를 삭제하고 이를 right_node로 옯겨준다.
                elif (i == self.cnt_key-1 and del_key >= self.key_list[self.cnt_key-1]):
                    #자식노드가 리프노드이면 prev_node, right_node 다시 연결
                    if (self.pair[self.key_list[0]].leaf == True):
                        child = self.right_node
                        child.prev_node.right_node = child.right_node
                        #완전 맨마지막 노드가 아닐경우에만
                        if (child.right_node != None):
                            child.right_node.prev_node = child.prev_node
                    self.right_node = self.pair[self.key_list[self.cnt_key-1]]
                    del self.pair[self.key_list[self.cnt_key-1]]
                    del self.key_list[self.cnt_key-1]
                    self.cnt_key-=1
                    return
            
        
    #해당 child노드가 몇번째 인덱스에 있는지 리턴하는 함수
    def find_NonLeaf(self, child_key):
        for i in range(self.cnt_key):
            if (self.key_list[i] > child_key):
                return i
            #가장 오른쪽 노드에 있을 경우 -1 반환
            elif (i == self.cnt_key-1 and child_key >= self.key_list[i]):
                return -1

    #키가 하나 있으며 자식 노드가 하나있는 노드
    def Empty_node(self, min_keys, max_keys, key, child):
        parent = self.parent
        idx = parent.find_NonLeaf(key)

        #왼쪽 형제 노드와 합치는 경우 -> 현재 노드가 부모 노드의 첫번째 노드만 아니면 됨
        if(idx != 0):
            #맨 오른쪽 노드의 경우
            if (idx == -1):
                Left = parent.pair[parent.key_list[parent.cnt_key-1]]
                Left.Add_NonLeaf(parent.key_list[parent.cnt_key-1], Left.right_node)
                Left.right_node = child
            else:
                Left = parent.pair[parent.key_list[idx-1]]
                #왼쪽 노드에 부모 노드의 키 값을 합침
                temp = {parent.key_list[idx-1] : Left.right_node}
                Left.pair.update(temp)
                Left.pair = sorted(Left.pair.items(), key = lambda t : t[0])
                Left.pair = dict(Left.pair)
                Left.cnt_key +=1
                Left.key_list.append(parent.key_list[idx-1])
                Left.key_list.sort()
                Left.right_node = child

            child.parent = Left

            #부모 노드가 완전히 지워지는 것을 예방하여 부모의 key와 child노드를 미리 저장함
            tmp_key = parent.key_list[0]

            #부모 노드에서 현재 노드를 지워야한다. (현재노드가 왼쪽 노드로 병합해있기 때문)   
            parent.Delete_NonLeaf(key)
            
            #만일 자식 노드가 리프노드라면 연결 다시해줘야함
            if(Left.pair[Left.key_list[0]].leaf == True):
                for i in range(Left.cnt_key-1):
                    Left.pair[Left.key_list[i]].right_node = Left.pair[Left.key_list[i+1]]
                #cnt_key-1의 경우
                Left.pair[Left.key_list[Left.cnt_key-1]].right_node = Left.right_node
                for i in range(1, Left.cnt_key):
                    Left.pair[Left.key_list[i]].prev_node =Left.pair[Left.key_list[i-1]]
                #right_node의 경우
                Left.right_node.prev_node = Left.pair[Left.key_list[Left.cnt_key-1]]
                Left.right_node.right_node = child.right_node
                if(child.right_node != None):
                    child.right_node.prev_node = Left.right_node

            #만일 부모 노드가 지워지고, 원래 부모 노드가 루트 노드였을 경우, 루트 노드 삭제, Left return
            if (Left.parent.cnt_key == 0 and Left.parent.parent == None and Left.cnt_key <= max_keys and Left.cnt_key >= min_keys):
                Left.parent = None

            child = Left

            return Left.Balance(min_keys, max_keys, tmp_key, child)
        
        #오른쪽 노드와 합쳐지는 경우 (idx가 0이면 오른쪽노드와 합침)
        else:
            if(parent.cnt_key==1): #만일 child node가 두개밖에 존재하지 않는경우, 부모의 right_node가 오른쪽 형제 노드임
                Right = parent.right_node
            else:
                Right = parent.pair[parent.key_list[1]]

            #오른쪽 노드에 부모 노드의 키 값을 합침
            Right.Add_NonLeaf(parent.key_list[idx], child)
            child.parent = Right

            #부모 노드가 완전히 지워지는 것을 예방하여 부모의 key와 child노드를 미리 저장함
            #이때 부모 노드는 루트 노드가 아님
            tmp_key = parent.key_list[0]
    
            #부모 노드에서 현재 노드를 지워야한다. (현재노드가 오른쪽 노드로 병합해있기 때문), 현재 노드는 비워져있으므로 ex_key 값 사용
            parent.Delete_NonLeaf(key)

            #만일 자식 노드가 리프노드라면 연결 다시해줘야함
            if(Right.pair[Right.key_list[0]].leaf == True):
                for i in range(Right.cnt_key-1):
                    Right.pair[Right.key_list[i]].right_node = Right.pair[Right.key_list[i+1]]
                Right.pair[Right.key_list[Right.cnt_key-1]].right_node = Right.right_node
                for i in range(1, Right.cnt_key):
                    Right.pair[Right.key_list[i]].prev_node =Right.pair[Right.key_list[i-1]]
                #right_node의 경우
                Right.right_node.prev_node = Right.pair[Right.key_list[Right.cnt_key-1]]

                Right.pair[Right.key_list[0]].prev_node = child.prev_node
                if(child.prev_node != None):
                    child.prev_node.right_node = Right.pair[Right.key_list[0]]
            child = Right

            #만일 부모 노드가 지워지고, 원래 부모 노드가 루트 노드였을 경우
            if (Right.parent.cnt_key == 0 and Right.parent.parent == None and Right.cnt_key <= max_keys and Right.cnt_key >= min_keys):
                Right.parent = None


            return Right.Balance(min_keys, max_keys, tmp_key, child)

    #부모 노드(현재 노드)가 키 범위 안에 들지 않을때 재조정하는 과정을 거쳐야한다. 
    #루트노드에 도달할때까지 반복한다.
    def Balance(self, min_keys, max_keys, key = None, child = None):
        #만일 해당 노드가 루트 노드인 경우, 재조정하지 않는다.
        if (self.parent == None):
            return self
        #만일 현재 키의 개수가 0개라면, 
        elif (self.cnt_key == 0):
            return self.Empty_node(min_keys, max_keys, key, child)
        else:
            #만일 해당 노드가 최소 키 범위보다 작은 경우, 이때 부모노드는 루트노드가 아니다
            if (self.cnt_key < min_keys):
                parent = self.parent
                index = parent.find_NonLeaf(self.key_list[0]) #index = 부모노드에서 현재 노드가 있는 index값

                #왼쪽 형제 노드와 합치는 경우 -> 현재 노드가 부모 노드의 첫번째 노드만 아니면 됨
                if(index != 0):
                    # 맨 오른쪽에 해당하는 노드인 경우
                    if (index == -1):
                        Left = parent.pair[parent.key_list[parent.cnt_key-1]]
                        Left.Add_NonLeaf(parent.key_list[parent.cnt_key-1], Left.right_node)
                    else:
                        Left = parent.pair[parent.key_list[index-1]]
                        #왼쪽 노드에 부모 노드의 키 값과 현재 노드를 합침
                        temp = {parent.key_list[index-1] : Left.right_node}
                        Left.pair.update(temp)
                        Left.pair = sorted(Left.pair.items(), key = lambda t : t[0])
                        Left.pair = dict(Left.pair)
                        Left.cnt_key +=1
                        Left.key_list.append(parent.key_list[index-1])
                        Left.key_list.sort()
                        
                    for i in range(self.cnt_key):
                        temp = {self.key_list[i] : self.pair[self.key_list[i]]}
                        Left.pair.update(temp)
                        Left.pair = sorted(Left.pair.items(), key = lambda t : t[0])
                        Left.pair = dict(Left.pair)
                        Left.cnt_key +=1
                        Left.key_list.append(self.key_list[i])
                        Left.key_list.sort()

                    Left.right_node = self.right_node

                    #부모 노드가 완전히 지워지는 것을 예방하여 부모의 key와 child노드를 미리 저장함
                    #이때 부모 노드는 루트 노드가 아님
                    key = parent.key_list[0]

                    child = Left
                    
                    #부모 노드에서 현재 노드를 지워야한다. (현재노드가 왼쪽 노드로 병합해있기 때문)
                    parent.Delete_NonLeaf(self.key_list[0])

                    #자식노드들을 부모노드 연결 
                    for i in range(Left.cnt_key):
                        Left.pair[Left.key_list[i]].parent = Left
                    Left.right_node.parent = Left

                    #만일 자식 노드가 리프노드라면 연결 다시해줘야함
                    if(Left.pair[Left.key_list[0]].leaf == True):
                        for i in range(Left.cnt_key-1):
                            Left.pair[Left.key_list[i]].right_node = Left.pair[Left.key_list[i+1]]
                        #cnt_key-1의 경우
                        Left.pair[Left.key_list[Left.cnt_key-1]].right_node = Left.right_node
                        for i in range(1, Left.cnt_key):
                            Left.pair[Left.key_list[i]].prev_node =Left.pair[Left.key_list[i-1]]
                        #right_node의 경우
                        Left.right_node.prev_node = Left.pair[Left.key_list[Left.cnt_key-1]]
                        Left.right_node.right_node = self.right_node.right_node
                        if(self.right_node.right_node != None):
                            self.right_node.right_node.prev_node = Left.right_node
                        
                    #만일 부모 노드가 지워지고, 원래 부모 노드가 루트 노드였을 경우, 루트 노드 삭제, Left return
                    if (Left.parent.cnt_key == 0 and Left.parent.parent == None and Left.cnt_key <= max_keys and Left.cnt_key >= min_keys):
                        Left.parent = None
                    
                    return Left.Balance(min_keys, max_keys, key, child)
                
                #오른쪽 노드에서 빌려오는 경우
                else:
                    if(parent.cnt_key==1): #만일 child node가 두개밖에 존재하지 않는경우, 부모의 right_node가 오른쪽 형제 노드임
                        Right = parent.right_node
                    else:
                        Right = parent.pair[parent.key_list[1]]

                    #오른쪽 노드에 부모 노드의 키 값과 현재 노드를 합침
                    Right.Add_NonLeaf(parent.key_list[index], self.right_node)
                    for i in range(self.cnt_key):
                        Right.Add_NonLeaf(self.key_list[i], self.pair[self.key_list[i]])
                    
                    #부모 노드가 완전히 지워지는 것을 예방하여 부모의 key와 child노드를 미리 저장함
                    key = parent.key_list[0]

                    #부모 노드에서 현재 노드를 지워야한다. (현재노드가 오른쪽 노드로 병합해있기 때문)
                    parent.Delete_NonLeaf(self.key_list[0])

                    #자식노드들을 부모노드 연결 
                    for i in range(Right.cnt_key):
                        Right.pair[Right.key_list[i]].parent = Right
                    Right.right_node.parent = Right

                    #만일 자식 노드가 리프노드라면 연결 다시해줘야함
                    if(Right.pair[Right.key_list[0]].leaf == True):
                        for i in range(Right.cnt_key-1):
                            Right.pair[Right.key_list[i]].right_node = Right.pair[Right.key_list[i+1]]
                        Right.pair[Right.key_list[Right.cnt_key-1]].right_node = Right.right_node
                        for i in range(1, Right.cnt_key):
                            Right.pair[Right.key_list[i]].prev_node =Right.pair[Right.key_list[i-1]]
                        #right_node의 경우
                        Right.right_node.prev_node = Right.pair[Right.key_list[Right.cnt_key-1]]
                        Right.pair[Right.key_list[0]].prev_node = self.pair[self.key_list[0]].prev_node
                        if(self.pair[self.key_list[0]].prev_node != None):
                            self.pair[self.key_list[0]].prev_node.right_node = Right.pair[Right.key_list[0]]

                    child = Right
                    
                    #만일 부모 노드가 지워지고, 원래 부모 노드가 루트 노드였을 경우
                    if (Right.parent.cnt_key == 0 and Right.parent.parent == None and Right.cnt_key <= max_keys and Right.cnt_key >= min_keys):
                        Right.parent = None

                    return Right.Balance(min_keys, max_keys, key, child)
                     
            #만일 해당 노드가 최대 키 개수를 넘은 경우, split후 부모노드에 합쳐진다.
            elif (self.cnt_key > max_keys):
                parent = self.parent
                top = self.split()
                #만일 부모 노드가 비워있는 경우, top이 저절로 parent가 된다.
                if (parent.cnt_key == 0):
                    parent.cnt_key = top.cnt_key
                    parent.pair = top.pair 
                    parent.key_list = top.key_list
                    parent.right_node = top.right_node
                                  
                else:
                    top_key = top.key_list[0]
                    for i in range(parent.cnt_key):
                        if (top_key < parent.key_list[i]):
                            parent.Add_NonLeaf(top.key_list[0], top.pair[top.key_list[0]])
                            parent.pair[parent.key_list[i+1]] = top.right_node
                        elif (top_key >= parent.key_list[i] and i==parent.cnt_key-1):
                            parent.Add_NonLeaf(top.key_list[0], top.pair[top.key_list[0]])
                            parent.right_node = top.right_node

                #top의 자식노드 부모로 잘 연결
                for i in range(top.cnt_key):
                    top.pair[top.key_list[i]].parent = parent
                top.right_node.parent = parent

                return parent.Balance(min_keys, max_keys, key, child)

            #만일 해당 노드의 키 개수가 범위 내에 존재하는 경우
            #부모노드로 계속해서 올라가면서 조건을 충족하는지 확인
            else:
                #만일 부모 노드가 지워졌을때 비워지며, 부모 노드가 루트노드인 경우
                if (self.parent.cnt_key == 0 and self.parent.parent == None):
                    self.parent = None
                    return self.Balance(min_keys, max_keys, key, child)
                #만일 부모 노드가 지워졌다면, Empty_node함수로
                elif (self.parent.cnt_key == 0):
                    return self.parent.Empty_node(min_keys, max_keys, key, child)
                #만일 부모 노드가 지워지지 않았다면 계속해서 조건을 충족하는지 확인
                else:
                    return self.parent.Balance(min_keys, max_keys, key, child)

class Leaf:
    def __init__(self):
        self.cnt_key = 0
        self.pair = {}  #{key: value}형태
        self.key_list = []
        self.right_node = None #오른쪽 형제 노드
        self.prev_node = None #왼쪽 형제 노드
        self.leaf = True
        self.parent = None #부모노드를 가리키는 변수

    # key-value pair를 리프노드에 추가하는 함수
    def Add_Leaf(self, input_key, input_value):
        #Node가 비어있는 경우, 처음으로 추가하는 경우
        if (self.cnt_key == 0 ):
            self.pair = {input_key : input_value}
            self.key_list = [input_key] #키 값만 따로 저장
            self.cnt_key+=1 #키 개수 하나 증가
            return 

        #Node에 pair이 존재하는 경우
        for key in self.pair.keys():
            #Node에서 해당하는 key를 찾은 경우: 입력 value값을 뒤에 추가해준다, 이때 키 리스트는 변화 없음
            #duplicate key 허용하지 않음
            if (key == input_key):
                print("Duplicated keys are not allowed!")
                break
            
            #해당하는 key를 찾지 못한 경우, 삽입 후 키 값을 기준으로 정렬
            else: 
                temp = {}
                temp[input_key] = input_value
                self.pair.update(temp)
                #키 값을 기준으로 정렬
                self.pair = sorted(self.pair.items(), key = lambda t : t[0])
                self.pair = dict(self.pair)
                #키 리스트 조정
                self.key_list.append(input_key)
                self.key_list.sort()
                self.cnt_key+=1 #키 개수 하나 증가
                break

    #리프노드의 두개로 쪼개고 부모 노드에 split key 넣어주기
    def split(self):
        Right = Leaf()

        mid = math.floor(self.cnt_key/2) #나누는 기준 mid는 key개수의 반으로 나눈다. 이때 나누기 2한 값에 내림한다.
        
        #Right 리프노드 데이터 정리
        for i in range(mid, self.cnt_key):
            Right.Add_Leaf(self.key_list[i], self.pair[self.key_list[i]])
        Right.right_node = self.right_node
        Right.prev_node = self

        temp_key_list = self.key_list
        temp_pair = self.pair

        Left = self
        Left.cnt_key = 0
        Left.pair = {}
        Left.key_list = []
        Left.leaf = True

        #Left 리프노드 데이터 정리
        for i in range(mid):
            Left.Add_Leaf(temp_key_list[i], temp_pair[temp_key_list[i]])
        Left.right_node = Right

        #중간 키 값이 리프노드가 아닌 부모노드가 됨. key값만 남아짐. 이 node를 top이라 하고 이를 반환한다
        top = Non_Leaf()
        top.cnt_key+=1
        top.pair = {Right.key_list[0] : Left}
        top.key_list = [Right.key_list[0]]
        top.right_node = Right

        #Left와 Right 부모 노드와 연결
        Left.parent = top
        Right.parent = top

        return top

    #해당 키 값이 리프 노드에 존재하는지 확인하는 함수
    def Search_Leaf(self, key):
        for i in range(self.cnt_key): #만일 리프노드에 찾고자 하는 키 값이 존재하는 경우
            if (key==self.key_list[i]):
                return i #node의 key_list에서의 인덱스 값을 반환
            elif (key != self.key_list[i] and i == self.cnt_key-1):
                return -1 #만일 존재하지 않으면 -1을 반환

    #노드에서 해당 인덱스에 해당하는 쌍을 삭제하는 함수
    def Delete_Leaf(self, index):
        self.cnt_key-=1
        prev_node = self.prev_node
        right_node = self.right_node

        #pair에서 해당 쌍을 삭제한다.
        del self.pair[self.key_list[index]]
        del self.key_list[index]

        self.pair = sorted(self.pair.items(), key = lambda t : t[0])
        self.pair = dict(self.pair)
        self.key_list.sort()

        if (index == 0):
            self.prev_node = prev_node
        elif (index == self.cnt_key or index == -1):
            self.right_node = right_node

        return self
    
    #형제 노드가 존재하는지 확인 (parent가 같은지 확인해야한다.)
    def isRight(self):
        if(self.right_node != None and self.parent == self.right_node.parent):
            return True
        else:
            return False

    #왼쪽 노드가 존재하는지 확인 
    def isPrev(self):
        if (self.prev_node != None and self.prev_node.parent == self.parent) :
            return True
        else:
            return False

    #왼쪽 형제 노드에서 키 값을 가져오는 경우
    def Borrow_From_Left(self, index):
        Left = self.prev_node
        L_key = Left.key_list[-1]
        ex_key = self.key_list[0]
        
        #원래 노드에 있던 key와 value 삭제
        self.Delete_Leaf(index)

        #노드에 형제 노드 키와 값 추가
        self.Add_Leaf(L_key, Left.pair[L_key])

        #형제 노드에서 마지막 값을 뺐으니, 이에 맞게 노드를 조정함
        Left = Left.Delete_Leaf(-1)

        #형제 노드의 마지막 key와 value를 가져왔음
        #따라서 부모 노드의 키 값이 바뀌어야 한다.
        self.parent.change(ex_key, L_key)

    #오른쪽 형제 노드에서 키 값을 가져오는 경우
    def Borrow_From_Right(self, index):
        Right = self.right_node
        R_key = Right.key_list[0]

        #원래 노드에 있던 key와 value 삭제
        self = self.Delete_Leaf(index)

        #노드에 형제 노드 키와 값 추가
        self.Add_Leaf(R_key, Right.pair[R_key])

        #형제 노드에서 첫번째 값을 뺐으니, 이에 맞게 노드를 조정함
        Right = Right.Delete_Leaf(0)

        #형제 노드의 첫번째 key와 value를 가져왔음
        #따라서 부모 노드의 키 값이 바뀌어야 한다.
        self.parent.change(R_key, Right.key_list[0])

    #형제 노드와 병합하는 함수
    def merge(self):
        #왼쪽 형제 노드가 존재해 왼쪽 노드와 병합하는 경우
        if (self.isPrev()):
            Left = self.prev_node
            for i in range(self.cnt_key):
                Left.Add_Leaf(self.key_list[i], self.pair[self.key_list[i]])
            Left.right_node = self.right_node
            #self.right_node가 존재한다면,
            if(self.right_node != None):
                self.right_node.prev_node = Left
            return Left
 
        #왼쪽 형제 노드가 존재하지 않아 오른쪽 노드와 병합하는 경우
        elif (self.isRight()):
            Right = self.right_node
            for i in range(self.cnt_key):
                Right.Add_Leaf(self.key_list[i], self.pair[self.key_list[i]])
            Right.prev_node = self.prev_node
            #완전 맨 처음 노드가 아닌경우
            if (self.prev_node != None):
                self.prev_node.right_node = Right
            return Right

        
class BPTree:
    def __init__(self, size):
        self.root = Leaf() #첫 번째 root노드는 무조건 리프 노드이다.
        self.size = int(size) #B+트리의 차수
        self.max_child = self.size #최대 자식의 수
        self.max_keys = self.max_child-1 #최대로 가질 수 있는 키의 개수
        self.min_keys = (math.ceil)(self.size/2.0)-1 #최소 키의 개수
    
    #해당 노드에서 키 값을 비교해 자리를 찾는 함수 (이때 부모노드와 비교한다고 보면 됨)
    def find(self, node, key):
        for i in range(node.cnt_key):
            #찾으려는 key값이 list에 있는 key값보다 작으면 왼쪽으로 이동한다.
            if (key < node.key_list[i]):
                return node.pair[node.key_list[i]]
            #찾으려는 key값이 list에 있는 key값과 같거나 크면 오른쪽으로 이동한다.
            elif (i+1 == node.cnt_key and node.key_list[i] <= key):
                return node.right_node

    #child Node가 parent Node에 합쳐지는 경우
    def merge(self, parent, child):
        index = child.key_list[0] #합쳐질 child의 키 값

        for i in range(parent.cnt_key):
            #child 노드의 키가 들어갈 자리를 찾아서 merge됨
            if (index < parent.key_list[i]):
                parent.cnt_key +=1
                temp ={}
                temp[index] = child.pair[index]
                parent.pair.update(temp)
                parent.pair = sorted(parent.pair.items(), key = lambda t : t[0])
                parent.pair = dict(parent.pair)
                parent.key_list.append(index)
                parent.key_list.sort()
                parent.pair[parent.key_list[i+1]] = child.right_node

                #child의 자식노드의 부모 노드가 parent로 변경이 됨
                child.pair[index].parent = parent #child의 왼쪽 자식의 경우
                child.right_node.parent = parent #child의 오른쪽 자식의 경우
                break
            
            #삽입하려는 child의 키가 parent 노드의 마지막일때 (child의 키가 가장 큼)
            elif (i+1 == parent.cnt_key):
                parent.cnt_key +=1
                temp ={}
                temp[index] = child.pair[index]
                parent.pair.update(temp)
                parent.pair = sorted(parent.pair.items(), key = lambda t : t[0])
                parent.pair = dict(parent.pair)
                parent.key_list.append(index)
                parent.key_list.sort()
                parent.right_node = child.right_node

                #child의 자식노드의 부모 노드가 parent로 변경이 됨
                child.pair[index].parent = parent #child의 왼쪽 자식의 경우
                child.right_node.parent = parent #child의 오른쪽 자식의 경우
                break

    #데이터를 삽입하는 함수
    def insert(self, key, value):
        #비쁠 트리의 루트노드에서부터 시작한다.
        child = self.root
        parent = None

        #삽입은 리프노드에서 이루어지기 때문에 리프노드인지 확인해봐야한다.
        while(child.leaf == False): #리프노드가 아니라면, 리프노드를 찾을때까지 while문 실행
            parent = child
            child = self.find(parent, key)
        
        #node가 리프노드임
        child.Add_Leaf(key, value)

        while(child.cnt_key > self.max_keys): #만일 노드에 수용할 수 있는 키의 개수를 넘어서면, split한다.
            if (child == self.root): #만일 child노드가 루트노드라면,
                child = child.split()
                self.root = child #자식 노드에서 쪼개져서 올라간 노드가 루트노드가 된다.
                break

            else: #만일 child가 루트노드가 아니라면
                parent = child.parent
                child = child.split()
                self.merge(parent, child)
                child = parent

    #해당 키가 있는 노드와 인덱스를 반환
    def search(self, key):
        #루트노드에서 시작해서 해당 키가 있는 리프 노드를 찾는다.
        child = self.root
        parent = None

        #리프노드인지 확인해야한다.
        while(child.leaf == False): #리프노드가 아니라면, 리프노드를 찾을때까지 while문 실행
            parent = child
            child = self.find(parent, key)
            
        #해당 키가 노드에 존재하는지 확인함, index는 지우려고 하는 키가 노드의 key_list에서 어느 인덱스에 있는지 반환함, -1이면 키가 노드에 존재하지 않음
        index = child.Search_Leaf(key)

        if (index==-1):
            print("Key {0} does not exist in this tree!".format(key))
            return
        
        else:
            return child, index #해당 키가 있는 노드와 인덱스를 반환

    #트리를 재구성하는 과정 (키값을 재조정)
    #부모 노드의 인덱스 값은 오른쪽 자식의 리프 노드에서 가장 작은 값이다.
    def restruct(self, node):
        if (node == None):
            print("This tree is empty!!")
            return
        if(node.leaf == True):
            return

        #키가 하나만 있을경우
        if (node.cnt_key == 1):
            child = node.right_node
            #리프노드로 갈때까지 이동
            while (child.leaf == False):
                child = child.pair[child.key_list[0]]
            #리프노드에서 제일 작은 값을 new_key
            new_key = child.key_list[0]
            node.pair[new_key] = node.pair.pop(node.key_list[node.cnt_key-1])
            node.key_list[node.cnt_key-1] = new_key

        #키가 여러개 있을 경우
        else:
            for i in range(node.cnt_key-1):
                #오른쪽 자식
                child = node.pair[node.key_list[i+1]]
                #리프노드로 갈때까지 이동
                while (child.leaf == False):
                    child = child.pair[child.key_list[0]]
                #리프노드에서 제일 작은 값을 new_key
                new_key = child.key_list[0]
                node.pair[new_key] = node.pair.pop(node.key_list[i])
                node.key_list[i] = new_key

            #node.key_list[node.cnt_key-1]의 경우, 오른쪽 자식 노드는 right_node이다.
            child = node.right_node
            #리프노드로 갈때까지 이동
            while (child.leaf == False):
                child = child.pair[child.key_list[0]]

            #리프노드에서 제일 작은 값을 new_key
            new_key = child.key_list[0]
            node.pair[new_key] = node.pair.pop(node.key_list[node.cnt_key-1])
            node.key_list[node.cnt_key-1] = new_key
        
        for j in range(node.cnt_key):
            print(node.key_list)
            self.restruct(node.pair[node.key_list[j]])
        self.restruct(node.right_node)
        
    #키에 해당하는 데이터를 삭제하는 함수
    def delete(self, key): #삭제하고자하는 키
        if (self.search(key) == None):
            return

        node, index = self.search(key)

        #만일 해당 노드가 루트 노드라면, 
        if(node.parent == None):
            node.Delete_Leaf(index)
            return

        #1. node에 key를 지웠을때 최소 키 개수를 넘을떄
        if (node.cnt_key > self.min_keys):
            node.Delete_Leaf(index)
        #2. node에 key를 지웠을때 최소 키 개수를 넘지 못할때
        else:
            #2-1) 형제 노드에서 원소 가져와서 재분배 (형제노드가 존재하며 형제 노드가 최소 key 개수 초과)
            #2-1-1) 왼쪽 노드에서 가져오는 경우
            if (node.isPrev() and node.prev_node.cnt_key > self.min_keys):
                node.Borrow_From_Left(index)
            #2-1-2) 오른쪽 노드에서 가져오는 경우
            elif (node.isRight() and node.right_node.cnt_key > self.min_keys):
                node.Borrow_From_Right(index)

            #2-2) 재분배 실패하면 형제 노드와 병합 (형제 노드 존재하며, 형제 노드의 키의 개수가 최소 key보다 작거나 같을때)
            else:
                #2-2-1) 부모 노드가 루트 노드이거나 부모 노드가 최소 key 개수 초과
                # key를 삭제한 후, 형제 노드와 병합 
                if (node.parent.cnt_key > self.min_keys):
                    del_key = node.key_list[0]
                    node.Delete_Leaf(index)
                    sib = node.merge()
                    
                    sib.parent.Delete_NonLeaf(del_key)

                #2-2-2) 부모 노드가 최소 key 개수보다 작거나 같을때 -> 재구조화가 이뤄져야한다.
                else:
                    #만일 부모 노드가 루트 노드인 경우
                    if (node.parent.parent == None):
                        if (node.parent.cnt_key == 1):
                            node.Delete_Leaf(index)
                            self.root = node.merge()
                            self.root.parent = None
                        else:
                            del_key = node.key_list[0]
                            node.Delete_Leaf(index)
                            sib = node.merge()
                            sib.parent.Delete_NonLeaf(del_key)

                    #만일 부모 노드가 루트 노드가 아닌 경우
                    else:
                        child_key = node.key_list[0]
                        node.Delete_Leaf(index)
                        child = node.merge()

                        key = node.parent.key_list[0]               
                        node.parent.Delete_NonLeaf(child_key)

                        if (node.parent.cnt_key == 0):
                            self.root = node.parent.Balance(self.min_keys, self.max_keys, key, child)
                            self.root.parent = None
                        else:
                            self.root = node.parent.Balance(self.min_keys, self.max_keys)
                            self.root.parent = None
        print(bpt.printTree(bpt.root))
  
        self.restruct(self.root)

    #단일 키 탐색 함수
    def Single_Search(self, key):
        #루트노드에서 시작해서 해당 키가 있는 리프 노드를 찾는다.
        child = self.root
        parent = None

        #삭제는 리프노드에서 이루어지기 때문에 리프노드인지 확인해봐야한다.
        while(child.leaf == False): #리프노드가 아니라면, 리프노드를 찾을때까지 while문 실행
            str_key = [str(a) for a in child.key_list]
            print(", ".join(str_key))

            parent = child
            child = self.find(parent, key)

        #해당 키가 노드에 존재하는지 확인
        #index는 지우려고 하는 키가 노드의 key_list에서 어느 인덱스에 있는지 반환함, -1이면 키가 노드에 존재하지 않음
        index = child.Search_Leaf(key)

        if (index==-1):
            print("NOT FOUND\n")
            return
        
        else:
            print(child.pair[child.key_list[index]]) #리프 노드에서 해당 value값을 출력한다.
            return 

    #범위 탐색 함수
    def Ranged_Search(self, start_key, end_key):
        #루트노드에서 시작해서 해당 키가 있는 리프 노드를 찾는다.
        child = self.root
        parent = None

        #리프노드인지 확인해봐야한다.
        while(child.leaf == False): #리프노드가 아니라면, 리프노드를 찾을때까지 while문 실행
            parent = child
            child = self.find(parent, start_key)
        #리프 노드의 첫번째 키가 end_key보다 커질때까지 오른쪽으로 이동
        while(child.key_list[0] <= end_key):
            for i in range(child.cnt_key):
                #키 리스트에서 범위에 해당하면, key와 value 출력
                if (child.key_list[i] >= start_key and child.key_list[i]<=end_key):
                    print("{0}, {1}".format(child.key_list[i], child.pair[child.key_list[i]]))

            if(child.right_node == None):
                return
            child = child.right_node
    
    def list_Leaf(self):
        #루트노드에서 시작해서 해당 키가 있는 리프 노드를 찾는다.
        child = self.root
        parent = None

        if (child == None):
            return
        #리프 노드의 가장 처음 노드를 찾아감
        while(child.leaf == False): #리프노드가 아니라면, 리프노드를 찾을때까지 while문 실행
            parent = child
            child = parent.pair[parent.key_list[0]]
        
        list_Leaf = {} #{key : value}의 집합
        while(True):
            list_Leaf.update(child.pair)
            if(child.right_node == None):
                return list_Leaf #{key : value}의 집합을 호출한다.
            child = child.right_node

    #트리를 출력하는 함수
    def printTree(self, node):
        if(self.root == None or self.root.cnt_key == 0 ):
            print("This Tree Is Empty")
            return 

        if (node.leaf == False): #리프노드가 아닌경우
            print(node.key_list)
            print("\n")
            for i in range(node.cnt_key):
                self.printTree(node.pair[node.key_list[i]])
                if (i+1 == node.cnt_key):
                    self.printTree(node.right_node)
                    print("\n")
        
        elif (node.leaf == True): #리프노드인 경우
            for i in range(node.cnt_key):
                print("key {0} : value {1}".format(node.key_list[i],node.pair[node.key_list[i]]))
            print("\n")
                
if __name__ == '__main__':
    option = sys.argv[1]

    #Data File Creation
    if option == '-c':
        print("Data File Creation")
        index_file = sys.argv[2]
        b = sys.argv[3]
        Saving = saving(b)

        #save
        with open(index_file, 'wb') as f:
            pickle.dump(Saving,f)

        sys.exit()

    #Insertion
    elif option == '-i':
        print("Insertion")
        index_file = sys.argv[2] #index file이 주어짐

        #load해서 {key:value}와 degree 정보를 알아낸다
        with open (index_file, 'rb') as f:
            Saving = pickle.load(f)
        #이를 토대로 BPTree를 만든다.
        bpt = Saving.createTree()

        data_file = sys.argv[3] #data file은 csv 형태로 주어짐
        f = open(data_file, 'r', encoding="utf-8")
        rdr = csv.reader(f)
        #index file에서 불러온 bpt에 data를 insert함
        for line in rdr:
            bpt.insert(int(line[0]), int(line[1])) #왜냐하면 key value 모두 int형
        f.close()

        #insert해서 만들어진 최종 bpt의 리프노드의 {key:value}로 출력
        #index file에 저장
        with open(index_file, 'wb') as f:
            result = bpt.list_Leaf()
            Saving.ClearPair()
            Saving.AddPair(result)
            pickle.dump(Saving, f)

        # 트리 구조 참고하고 싶으시면 주석 푸세요!
        # bpt.printTree(bpt.root) 

        sys.exit()

    #Deletion
    elif option == '-d':
        print("Deletion")
        index_file = sys.argv[2] #index file이 주어짐

        #load
        with open (index_file, 'rb') as f:
            Saving = pickle.load(f)
        #이를 토대로 BPTree를 만든다.
        bpt = Saving.createTree()

        data_file = sys.argv[3] #data file은 csv 형태로 주어짐
        f = open(data_file, 'r', encoding="utf-8")
        rdr = csv.reader(f)
        #만든 bpt에 data를 delete함
        for line in rdr:
            bpt.delete(int(line[0])) #왜냐하면 key int형
        f.close()

        #delete해서 만들어진 최종 bpt의 리프노드의 정보를 {key:value}로 출력
        #index file에 저장
        with open(index_file, 'wb') as f:
            result = bpt.list_Leaf()
            Saving.ClearPair()
            Saving.AddPair(result)
            pickle.dump(Saving, f)

        # 트리 구조 참고하고 싶으시면 주석 푸세요!
        # bpt.printTree(bpt.root) 

        sys.exit()

    #Single Key Search
    elif option == '-s':
        print("Sing key Search")
        index_file = sys.argv[2]
        key = sys.argv[3]
        key = int(key)

        #load
        with open (index_file, 'rb') as f:
            Saving = pickle.load(f)
        #이를 토대로 BPTree를 만든다.
        bpt = Saving.createTree()

        bpt.Single_Search(key)

        #그냥 결과값만 출력하고 index file의 정보를 바꾸지 않는다.
        sys.exit()

    #Ranged Search
    elif option == '-r':
        print("Ranged Search")
        index_file = sys.argv[2]
        start_key = sys.argv[3]
        end_key = sys.argv[4]
        start_key = int(start_key)
        end_key = int(end_key)

        #load
        with open (index_file, 'rb') as f:
            Saving = pickle.load(f)
        #이를 토대로 BPTree를 만든다.
        bpt = Saving.createTree()

        bpt.Ranged_Search(start_key, end_key)

        #그냥 결과값만 출력하고 index file의 정보를 바꾸지 않는다.
        sys.exit()
