# -*- coding: utf-8 -
# (c) M. Maahn, 2017

from . import pamtraRadarMomentsLib
from . import decorators

import numpy as np


__version__ = '0.1'


def calc_hildebrandSekhon(spectrum, no_ave = 1,verbose=0):

  """
  Calculate the mean and maximum of noise of the linear radar spectrum following Hildebrand and Sekhon 1974.

  Parameters
  ----------

  spectrum : array_like
      linear radar spectrum. Can be 1D or 2D.
  no_ave : int, optional
      number of averages (default 1)
  verbose : int, optional
      verbosity level (default 0)

  Returns
  -------

  meanNoise : array_like or float
    mean noise level in linear units
  maxNoise : array_like or float
    maximum noise level in linear units
 
  """

  spectrum = np.asarray(spectrum)
  specShape = np.shape(spectrum)

  assert len(specShape) <=2,  'spectrum must not have more than two dimensions (height, nfft)'

  if len(specShape) == 1:
    spectrum = spectrum.reshape((1,specShape[0]))

  pamtraRadarMomentsLib.report_module.verbose = verbose

  error, meanNoise, maxNoise = pamtraRadarMomentsLib.hildebrand_sekhon(spectrum,no_ave)
  
  if error>0:
    raise RuntimeError('Error in Fortran routine hildebrand_sekhon')

  return meanNoise, maxNoise



@decorators.NDto2DtoND(referenceIn=0,convertInputs=[0],convertOutputs=[0,1,2,3,4])
def calc_radarMoments(spectrum,
    verbose = 0, 
    max_v = 7.885, 
    min_v = -7.885, 
    no_ave = 150, 
    npeaks = 3, 
    noise_distance_factor = 0, 
    noise_mean = None, #linear noise per spectral bin in mm6/m3
    noise_max = None, #linear noise per spectral bin in mm6/m3
    peak_min_snr=-10, 
    peak_min_bins=2, 
    smooth_spectrum= True,
    use_wider_peak=False,
    receiver_miscalibration=0,
    ):
  
  """
  Calculates the moments, slopes and edges of the linear radar spectrum. 

  Parameters
  ----------

  spectrum : array_like
      linear radar spectrum [mm⁶/m³]. Can be 1D or 2D.
  verbose : int, optional
      verbosity level (default 0)
  max_v : float, optional
    Maximum Nyquist Velocity (default  7.885)
  min_v : float, optional
    Minimum Nyquist Velocity (default  -7.885)
  no_ave : int, optional
    No of averages per spectrum (default  150)
  npeaks : int, optional
    No of peaks which should be determined (default  3)
  noise_distance_factor : float, optional
    factor between noise and noise max. If 0, noiase max is obtained using calc_hildebrandSekhon (default  0)
  noise_mean : array_like or float, optional
    linear mean noise per spectral bin in mm: mm6/m3. If None, it is determined using calc_hildebrandSekhon (default  None)
  noise_max : array_like or float, optional
    linear maximum noise per spectral bin in mm: mm6/m3. If None, it is determined using calc_hildebrandSekhon (default  None)
  peak_min_snr: float, optional
    minimum linear SNR for each peak (default 1.2)
  peak_min_bins: int, optional
    minimal number of bins per peak (default 2)
  smooth_spectrum: bool, optional
    smooth spectrum before estiamting moments (default  True)
  use_wider_peak: bool, optional
    include edges into peak (default False)
  receiver_miscalibration, float, optional
    simulate a wrong radar receiver calibration [dB] (default 0)
  Returns
  -------

  spectrum_out : array_like
    radar spectrum with noise removed [mm⁶/m³]
  moments : array_like
    0th - 4th moment [mm⁶/m³, m/s, m/s,-,-]
  slope : array_like
    slope of the peak [dB/(m/s)]
  edge : array_like
    left(0) and right(1) edge the peak [m/s]
  quality : array_like
    quality flag: 1st byte: aliasing; 2nd byte: more peaks present; 7th: no peak found; 8th: principal peak isolated
  noise_mean : float
    mean noise level in linear units

 """

  spectrum = np.asarray(spectrum)
  specShape = np.shape(spectrum)


  assert len(specShape) <=2, 'spectrum must not have more than two dimensions (height, nfft)'

  if (noise_mean is None):
    noise_mean, noise_maxHilde = calc_hildebrandSekhon(spectrum, no_ave = no_ave,verbose=verbose)
  if (noise_max is None):
    if noise_distance_factor > 0:
      noise_max = noise_mean * noise_distance_factor
    else:
      noise_max = noise_maxHilde


  noise_mean = np.asarray(noise_mean)
  noise_max = np.asarray(noise_max)

  pamtraRadarMomentsLib.report_module.verbose = verbose

  #apply a receiver miscalibration:
  if receiver_miscalibration != 0:
    spectrum = spectrum * 10**(0.1*receiver_miscalibration)
    noise_max = noise_max * 10**(0.1*receiver_miscalibration)
    noise_mean = noise_mean * 10**(0.1*receiver_miscalibration)

  if len(specShape) == 1:
    spectrum = spectrum.reshape((1,specShape[0]))
    noise_mean = noise_mean.reshape(1)
    noise_max = noise_max.reshape(1)

  assert (len(spectrum.shape) -1) == len(noise_mean.shape), 'shape of spectrum and noise_mean does not match'
  assert (len(spectrum.shape) -1) == len(noise_max.shape), 'shape of spectrum and noise_max does not match'


  output = pamtraRadarMomentsLib.calc_moments.calc_moments_column(
    npeaks,
    spectrum,
    noise_mean,
    noise_max,
    max_v,
    min_v,
    smooth_spectrum,
    use_wider_peak,
    peak_min_bins,
    peak_min_snr,
    )

  error,spectrum_out,moments,slope,edge,quality = output
  if error>0:
    raise RuntimeError('Error in Fortran routine calc_moments_column')

  return spectrum_out,moments,slope,edge,quality,noise_mean

