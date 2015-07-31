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
        return Coordinates.corners
    
#     change the perspective look of an image
class Perspective(object):
    def __init__(self, source):
        self.source = source
        
#     get the destinations and edges
    def handle(self):
        img = self.source
        self.shape = img.shape
#         print self.shape
        width = self.shape[1]
        print width
        height = self.shape[0]
        print height 
        self.destination = np.float32([[0,0], [width, 0],  [width, height], [0, height]])
        print self.destination
#         if y < 300 and x < 400: 
#             img = cv2.pyrUp(img)
#         else:
#             img = cv2.pyrDown(img)two
#         gray = cv2.cvtColor(img, cv2.cv.CV_BGR2GRAY)
        edges = cv2.Canny(img, 100, 150)
#         print edges
#         cv2.imshow("edges", edges)
#         cv2.waitKey(0)
        cv2.namedWindow("image", cv2.CV_WINDOW_AUTOSIZE)
        return edges
        
#         find the hull/ contour and the intersection points
    def contourmethod(self, edges):
        hull = None
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print hierarchy 
        for i, cnt in enumerate(contours):
            if hierarchy[0,i,3] == -1 and cv2.contourArea(cnt) > 5000:
                hull = cv2.convexHull(cnt, returnPoints=True)
                break
        print hull
        length = len(hull)
        
        print length
        coord = Coordinates()
        for i in xrange(0, length):
            if (i + 3) < length:
                [x, y] = coord.intersection((hull[i][0][0], hull[i][0][1]), (hull[i + 1][0][0], hull[i + 1][0][1]), (hull[i + 2][0][0], hull[i + 2][0][1]), (hull[i + 3][0][0], hull[i + 3][0][1]))
                coord.append(x, y)
        return coord
    
#     transform the points to the destination and return warped image and transformationMatrix
    def transform(self, corners):
        corners = np.float32((corners[0][0], corners[1][0], corners[2][0], corners[3][0]))
#         print "transform", corners[0][0], corners[1][0], corners[2][0], corners[3][0]
#         corners = np.float32(corners)
        transformationMatrix = cv2.getPerspectiveTransform(corners, self.destination)
        minVal = np.min(self.destination[np.nonzero(self.destination)])
        print "minVal", minVal, "width",self.shape[0]
        maxVal = np.max(self.destination[np.nonzero(self.destination)])
        print "maxVal", maxVal, "height",self.shape[1]
        warpedImage = cv2.warpPerspective(self.source, transformationMatrix, (self.shape[1], self.shape[0]))
        return warpedImage, transformationMatrix
        
#         improve the image by sharpening it
    def showsharpen(self, warpedImage):
        cv2.imshow("image", warpedImage)
        cv2.waitKey(0)
        # gray = cv2.cvtColor(warpedImage, cv2.cv.CV_BGR2GRAY)
        blur = cv2.GaussianBlur(warpedImage, (5, 5), 2)
        alpha = 1.5
        beta = 1 - alpha #1 - alpha
        gamma = 0
        sharpened = cv2.addWeighted(warpedImage, alpha, blur, beta, gamma)
        cv2.imshow("sharpened", sharpened)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    source = cv2.imread("card.jpg", 0)
    persp = Perspective(source)
    edges = persp.handle()
    contourcoord = persp.contourmethod(edges)
    if contourcoord.quadcheck():
        contourcoord.calculateCentroid()
        corners = contourcoord.calculateTRTLBRBL()
        warpedImage, transformationMatrix = persp.transform(corners)
        persp.showsharpen(warpedImage)
