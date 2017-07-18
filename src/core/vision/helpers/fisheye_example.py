import fisheye
import os
import glob
import cv2

base_path = r'../../../../parameters/environment_camera_calib'
calib_file = base_path + 'calib.dat'
NX, NY = 9, 6


def main():
    imgs_paths = glob.glob(os.path.join(base_path, '*.jpg'))
    #print os.path.join(base_path, '*.jpg')
    #print imgs_paths
    
    if not os.path.isfile( calib_file ):
        imgs_paths = imgs_paths[0:10]
        
        fe = fisheye.FishEye(nx=NX, ny=NY, verbose=True)
        
        rms, K, D, rvecs, tvecs = fe.calibrate(
            imgs_paths,
            show_imgs=True
        )
        
        fe.save( calib_file )
    else:
        fe = fisheye.FishEye.load( calib_file )

    #new_matrix, roi = cv2.getOptimalNewCameraMatrix( self._K, self._D, (w,h), 0, (w,h))
    #new_matrix = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(self._K, self._D, (w,h), None, new_matrix, balance=1#,fov_scale=1)
    #K = new_matrix
            
    img = cv2.imread(imgs_paths[0])
    
    
    undist_img = fe.undistort(img)
    undist_img = cv2.resize( undist_img, (0,0), fx=0.5, fy=0.5)
    cv2.imshow('undistorted', undist_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

if __name__ == '__main__':
    main()