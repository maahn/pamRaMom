# -*- coding: utf-8 -*-

from functools import wraps
from copy import deepcopy
import numpy as np




def NDto2DtoND(referenceIn=0,noOfInDimsToKeep=1, convertInputs=[0],convertOutputs=[0],verbosity=0):
  """
  Decorator to turn the Pamtra functions which expect only one dimension 
  (usually height) into function accepting arbritrary shapes.

  Parameters
  ----------

  referenceIn : int, optional
      Input argument used as reference for reshaping (default 0)
  noOfInDimsToKeep : int, optional
      number of dimensions to preserve of referenceIn (counting from the back) (default 1)
  convertInputs : list of int, optional
      list of indices of input arguments which should be treated. (default [0])
  convertOutputs : list of int, optional
      list of indices of output arguments which should be treated. (default [0])
  verbosity : int, optional
      verbosity level (default 0)
  Returns
  -------

  function : function
    decorated function

  """
  def NDto2DtoND_decorator(func):
    @wraps(func)
    def inner(*args, **kwargs):
      if verbosity>0: print ('decorating %s'%func.__name__)
      referenceShape = None
      addDims = False
      args = list(args)
      for ii in convertInputs:
        args[ii] = np.asarray(args[ii])
        inShape = args[ii].shape
        #special case we have to add dimensions
        if len(inShape) == noOfInDimsToKeep:
          inShapeNew = (1,) + inShape
          addDims = True
        # we remove dimensions
        else:
          #nothing to keep, just add
          if noOfInDimsToKeep == 0:
            inShapeKeep = ()
          #find out which needs to be untouched
          else:
            inShapeKeep = inShape[-noOfInDimsToKeep:]
          inShapeFlatten = inShape[:len(inShape)-noOfInDimsToKeep]
          #the reference to reshpe the output
          if (ii == referenceIn):
            referenceShape = deepcopy(inShapeFlatten)
          inShapeNew = (np.prod(inShapeFlatten).astype(int),) + inShapeKeep
        if verbosity > 0: print('in',ii,inShape,inShapeNew,referenceShape)
        args[ii] = args[ii].reshape(inShapeNew)
      result =  func(*args, **kwargs)
      #make sure output containes more than variable, otherwise make it iterable
      if not isinstance(result,tuple):
        result = (result,)
      result = list(result)
      for oo in convertOutputs:
        result[oo] = np.asarray(result[oo])
        outShape = result[oo].shape
        #special case we had to add dimensions, now remove it
        if addDims:
          outShapeNew =  outShape[1:]
        else:
          outShapeNew = referenceShape+outShape[1:]
        if verbosity > 0: print('out',oo,outShape,outShapeNew,referenceShape)
        result[oo] = result[oo].reshape(outShapeNew)
      result = tuple(result)
      if len(result) == 1:
        result = result[0]
      return result
    return inner
  return NDto2DtoND_decorator

