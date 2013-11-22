import cv2
import numpy

class BaseFeatureDetector(object):
    def __init__(self, params):
        self.params = params
    def run(self, image_filename):
        pass
    
class SurfFeatureDetector(BaseFeatureDetector):
    def __init__(self, params):
        super(SurfFeatureDetector, self).__init__(params)
        self.surf_detector = cv2.SURF(hessianThreshold = self.params['hessian_threshold'])
    
    def run(self, img): # img is a numpy matrix
        keypoints = self.surf_detector.detect(img, None)
        return keypoints
        
class BaseFeatureDescriptor(object):
    def __init__(self):
        #self.params = params
        pass
    def run(self, image_filename):
        pass
class SurfFeatureDescriptor(BaseFeatureDescriptor):    
    def __init__(self):
        self.surf_descriptor = cv2.DescriptorExtractor_create("SURF")
        
    def run(self, img, keypoints):
        floc,fdesc = self.surf_descriptor.compute(img, keypoints) # returns empty result
        return floc, fdesc
 
class RawFeatureDescriptor(BaseFeatureDescriptor):
    pass

if __name__ == '__main__':

    from Viblio.common import config
    filename = config.resource_dir() + '/features/sample_img_001.jpg' 
    
    # read the image and convert to gray
    imgo = cv2.imread(filename)
    img = cv2.imread(filename, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    
    params = {}
    params['hessian_threshold'] = 5000
    
    # set-up the feature extractor and descriptor
    surf_detector = SurfFeatureDetector(params)
    surf_descriptor  = SurfFeatureDescriptor()
    
    keypoints = surf_detector.run(img)
    floc, fdesc = surf_descriptor.run(img, keypoints)
    
    pts = [(int(x.pt[0]), int(x.pt[1])) for x in floc]
    
    feature_data = {}
    feature_data['pts'] = pts
    feature_data['fdesc'] = fdesc
    
    import pickle
    feat_filename = config.resource_dir() + '/features/sample_img_001.feat' 
    output = open(feat_filename, 'wb')
    pickle.dump(feature_data, output)
    output.close()
    
    #display
    for xx in floc:
        cv2.circle(imgo, (int(xx.pt[0]), int(xx.pt[1])), 1, (0, 0, 255))
    from matplotlib import pylab
    cv2.imshow("features", imgo)
    cv2.waitKey(0)