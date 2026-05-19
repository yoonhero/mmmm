import numpy as np
import matplotlib.pyplot as plt

points = [
    [0,0],
    [0,3],
    [4,0]
] # (3,4,5)
points = np.array(points)

parameter = np.array([1,1,1]) # a,b,r for (x-a)^2+(y-b)^2=r^2
def update(parameter):
    # extend Newton-raphson idea
    #   (x1-a)^2+(y1-b)^2-r^2 = 0
    #   ...
    #   (xn-a)^2+(yn-b)^2-r^2 = 0
    Y = np.empty(3)
    for i in range(3):
        Y[i]=np.sum((points[i]-parameter[:2])**2)-parameter[2]**2
    Jacobian = np.empty((3,3))
    Jacobian[:,0]=2*(parameter[0]-points[:,0])
    Jacobian[:,1]=2*(parameter[1]-points[:,1])
    Jacobian[:,2]=-2*parameter[2]

    # projective_matrix = np.linalg.inv(Jacobian.T@Jacobian) @ Jacobian.T
    # P=projective_matrix@Y
    delta=np.linalg.solve(Jacobian,Y)
    return parameter-delta

for _ in range(10):
    parameter=update(parameter)

    print(parameter)