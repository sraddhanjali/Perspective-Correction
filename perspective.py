import cv2
import numpy as np

from coordinates import Coordinates

#     change the perspective look of an image
class Perspective(object):
    def __init__(self, source):
        self.source = source

    def set_destination(self, img):
        self.shape = img.shape
#         print self.shape
        width = self.shape[1]
        print width
        height = self.shape[0]
        print height 
        self.destination = np.float32([[0, 0], [width, 0],  [width, height], [0, height]])
        print self.destination
        
#     get the destinations and edges
    def handle(self):
        img = self.source
        self.set_destination(img)
        edges = cv2.Canny(img, 100, 200, apertureSize=3)
        # cv2.imshow("edges", edges)
        # cv2.waitKey(0)
        # cv2.namedWindow("image", cv2.CV_WINDOW_AUTOSIZE)
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

    def get_coordinates_houghP(self, edges):
        constant = 100
        minLineLength = 10
        maxLineGap = 5
        coord = Coordinates()
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, constant, minLineLength, maxLineGap)
        print lines, type(lines)
        points = []
        for x1, y1, x2, y2 in lines[0]:
            points.append([x1, y1])
            points.append([x2, y2])

        [x, y] = coord.intersection(points[0], points[1], points[2], points[3])
        coord.append(x, y)
            # cv2.line(edges, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # cv2.imshow("line", edges)
        # cv2.waitKey(0)
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