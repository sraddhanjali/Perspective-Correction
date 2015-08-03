import cv2
import numpy as np

#coordinates of the number of intersections obtained
class Coordinates(object):
    coord = []
    size = -1

    def __init__(self):
        Coordinates.size += 1
        Coordinates.centroidx = 0
        Coordinates.centroidy = 0
        Coordinates.sumx = 0
        Coordinates.sumy = 0
        Coordinates.corners = []
        Coordinates.quad = 4

    def centroidxy(self, x, y):
        Coordinates.sumx += x
        Coordinates.sumy += y        
         
#     append the coordinates of intersections
    def append(self, x, y):
        self.centroidxy(x, y)
        Coordinates.coord.append([x, y])
        Coordinates.size += 1
    
#     check if the points make up a quadrilateral    
    def quadcheck(self):
        Coordinates.coord = np.reshape(Coordinates.coord, (Coordinates.size, 1, 2))
        peri = cv2.arcLength(Coordinates.coord, True)
        approx = cv2.approxPolyDP(Coordinates.coord, 0.1*peri, True)
        print approx, "approx", len(approx)
        if len(approx) == Coordinates.quad:
            print "yes a quad"
            Coordinates.coord = approx.tolist()
            return True
        else:
            print "not a quad"
            Coordinates.coord = approx.tolist()
            return False
        
#     find the centroid of the points of intersections found
    def calculateCentroid(self): 
        Coordinates.centroidx = Coordinates.sumx/Coordinates.size
        Coordinates.centroidy = Coordinates.sumy/Coordinates.size
        print "centroids", Coordinates.centroidx, Coordinates.centroidy

#     find the intersection points of all the hull structures found            
    def intersection(self, P1, P2, P3, P4):
        x1 = P1[0]
        y1 = P1[1]
        x2 = P2[0]
        y2 = P2[1]
        x3 = P3[0]
        y3 = P3[1]
        x4 = P4[0]
        y4 = P4[1]
        d = (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        if d:
            inter_X = ((x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2) * (x3*y4 - y3*x4)) / d
            inter_Y = ((x1*y2 - y1*x2) * (y3 - y4) - (y1 - y2) * (x3*y4 - y3*x4)) / d
        
        print "intersections",  inter_X, inter_Y
        return [inter_X, inter_Y]         
    
#     find the Top right, Top left, Bottom right and Bottom left points
    def calculateTRTLBRBL(self):
        topoints = []
        bottompoints = []
        for coord in Coordinates.coord:
            print coord, type(coord)
            if coord[0][1] < Coordinates.centroidy:
                topoints.append(coord)
            else: 
                bottompoints.append(coord)
        
        top_left = min(topoints)
        top_right = max(topoints)
        bottom_right = max(bottompoints)
        bottom_left = min(bottompoints)
        
        Coordinates.corners.append(top_left)
        Coordinates.corners.append(top_right)
        Coordinates.corners.append(bottom_right)
        Coordinates.corners.append(bottom_left)
        print Coordinates.corners
        return Coordinates.corners