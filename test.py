# from typing import Type


# def findXor(x, y):
#     return (x | y) - (x & y)


# def findOr(x,y):
#     return (x|y)

# def Solve(N,Q,A,Type,L,R):
#     s =0
#     a = A
#     for q in range(Q):
       
#         for i in range(len(A)):
#             print(L,R,i,len(A))
#             if i<len(L):
#                 if i+1 >= L[i] and i+1<=R[i]:
#                     if Type[q] == 1:
#                         a.insert(i,findOr(A[i],A[i]-1))
                        
#                     elif Type==2:
#                         a.insert(i,findXor(A[i],A[i]-1))
                    
#                 else:
#                     if len(L):
#                         a.insert(i,A[i])
#                 a.pop()
#                 a.pop()
#                 s+=sum(a)
#                 print(s)
#                 print(a)
#     return s
#         # for i in range(L[q]-1,R[q]-1):

# N= 4
# Q=2
# A = [5,4,8,6]
# Typ= [1,2]
# L=[1,2]
# R=[3,2]
# print(Solve(N,Q,A,Typ,L,R))

# import requests

# url = "https://barcode-lookup.p.rapidapi.com/v3/products"

# headers = {
#     'x-rapidapi-host': "barcode-lookup.p.rapidapi.com",
#     'x-rapidapi-key': "ffc135b1d6msh48ed5e2971128a5p1f3e65jsn0408bb956706"
#     }

# response = requests.request("GET", url, headers=headers)

# print(response.text)


# import requests

# url = "https://gs1parser.p.rapidapi.com/parse"

# querystring = {"q":"(01)12345678901231(10)ABCD-123(30)27(11)211015"}

# headers = {
#     'x-rapidapi-host': "gs1parser.p.rapidapi.com",
#     'x-rapidapi-key': "ffc135b1d6msh48ed5e2971128a5p1f3e65jsn0408bb956706"
#     }

# response = requests.request("GET", url, headers=headers, params=querystring)

# print(response.text)