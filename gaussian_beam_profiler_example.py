# Imports from the python standard library:
import time

# Third party imports, installable via pip:
from tifffile import imread, imwrite

# Our code, one .py file per module, copy files to your local directory:
# https://github.com/amsikking/coherent_OBIS_LSLX_laser_box
import coherent_OBIS_LSLX_laser_box
import gaussian_beam_profiler as gbp
import thorlabs_CS165MU1 # https://github.com/amsikking/thorlabs_CS165MU1

# init devices:
camera = thorlabs_CS165MU1.Camera(verbose=True, very_verbose=False)
lasers = {'405':1, '445':2, '488':3, '561':4, '640':5}
laser_box = coherent_OBIS_LSLX_laser_box.Controller(
    which_port='COM22', name2channel=lasers, verbose=False, very_verbose=False)

# configure devices:
camera.apply_settings(
    ch=0, num_images=1, exposure_us=1000, height_px='max', width_px='max')
laser = '488'
laser_box.set_power_setpoint(1, laser)

# acquire and get beam  diameter:
continuous = True # measure once or continously?
laser_box.set_enable('ON', laser)
laser_box.get_power(laser)
camera.verbose = False
try:
    while True:
        image = camera.record_to_memory(0)[0]
        # fit guassian and get parameters
        xp, yp = gbp.fit_gaussian(image, verbose=False, plot=False)
        # get beam diameters in x and y:
        x_d0_mm, y_d0_mm = gbp.get_beam_diameter_mm((xp, yp), um_per_px=3.45)    
        if not continuous:
            break
        else:
            print('("Ctrl-C" to exit)')
            time.sleep(1)
except KeyboardInterrupt:
    pass
camera.verbose = True
laser_box.set_enable('OFF', laser)

# save profile:
imwrite('beam_profile.tif', image, imagej=True)

# close:
camera.close()
laser_box.close()
