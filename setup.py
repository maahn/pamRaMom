import os
import sys
from numpy.distutils.misc_util import Configuration
from numpy.distutils.core import setup




def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def configuration(parent_package='',top_path=None):
    
    config = Configuration('pamtraRadarMoments', parent_package, top_path,
        version = '0.1',
        author  = "Maximilin Maahn",
        author_email = "maximilian.maahn@colorado.edu",
        description = "Estimate Moments from a radar Doppler spectrum",
        license = "GPL v3",
        python_requires='>=3.5',
        url = 'https://github.com/maahn/pamtraRadarMoments',
        download_url = 'https://github.com/maahn/pamtraRadarMoments/releases/download/0.1/pamtraRadarMoments-0.1.zip',
        long_description = read('README.rst'),
        classifiers = [
            "Development Status :: 3 - Alpha",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Fortran",
            "Programming Language :: Python",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering :: Atmospheric Science",
            ]
    )

    kw = {}
    if sys.platform == 'darwin':
        kw['extra_link_args'] = ['-undefined dynamic_lookup', '-bundle']
    config.add_extension('pamtraRadarMomentsLib',
        sources=[
                 'pamtraRadarMoments/pamtraRadarMomentsLib/pamtraRadarMomentsLib.pyf',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/kinds.f90',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/report_module.f90',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/constants.f90',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/convolution.f90',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/dsort.f90',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/hildebrand_sekhon.f90',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/smooth_savitzky_golay.f90',
                 'pamtraRadarMoments/pamtraRadarMomentsLib/calc_moments.f90',
                 ],
        library_dirs = ['../dfftpack/'],
        libraries = ['dfftpack','lapack'],
        **kw)

    return config


if __name__ == "__main__":

    
    setup(configuration=configuration,
        packages = ['pamtraRadarMoments','pamtraRadarMoments.pamtraRadarMomentsLib'],        
        # package_data = {
        #     'pamtraRadarMoments': ['file'],
        # },
        platforms = ['any'],
        requires = ['numpy', 'scipy'])

