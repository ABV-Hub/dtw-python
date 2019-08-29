##
## Copyright (c) 2006-2019 of Toni Giorgino
##
## This file is part of the DTW package.
##
## DTW is free software: you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## DTW is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
## or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
## License for more details.
##
## You should have received a copy of the GNU General Public License
## along with DTW.  If not, see <http://www.gnu.org/licenses/>.
##


# Author: Toni Giorgino 2018
#
# If you use this software in academic work, please cite:
#  * T. Giorgino. Computing and Visualizing Dynamic Time Warping
#    Alignments in R: The dtw Package. Journal of Statistical
#    Software, v. 31, Issue 7, p. 1 - 24, aug. 2009. ISSN
#    1548-7660. doi:10.18637/jss.v031.i07. http://www.jstatsoft.org/v31/i07/


import numpy
import sys

from .stepPattern import *
from ._backtrack import _backtrack
from ._globalCostMatrix import _globalCostMatrix
from .window import *
from .dtwPlot import *

from scipy.spatial.distance import cdist


# --------------------

class DTW:
    def __init__(self, obj):
        self.__dict__.update(obj)  # Convert dict to object

    def __repr__(self):
        s = "DTW alignment object of size (query x reference): {:d} x {:d}".format(self.N, self.M)
        return (s)

    def plot(self, type="alignment", **kwargs):
        # IMPORT_RDOCSTRING plot.dtw
        """Plotting of dynamic time warp results




Methods for plotting dynamic time warp alignment objects returned by
[dtw()].




**Details**

``dtwPlot`` displays alignment contained in ``dtw`` objects.

Various plotting styles are available, passing strings to the ``type``
argument (may be abbreviated):

-  ``alignment`` plots the warping curve in ``d``;
-  ``twoway`` plots a point-by-point comparison, with matching lines;
   see [dtwPlotTwoWay()];
-  ``threeway`` vis-a-vis inspection of the timeseries and their warping
   curve; see [dtwPlotThreeWay()];
-  ``density`` displays the cumulative cost landscape with the warping
   path overimposed; see [dtwPlotDensity()]

Additional parameters are passed to the plotting functions: use with
care.





Parameters
----------
x,d : 
    `dtw` object, usually result of call to [dtw()]
xlab : 
    label for the query axis
ylab : 
    label for the reference axis
type : 
    general style for the plot, see below
plot_type : 
    type of line to be drawn, used as the `type` argument
in the underlying `plot` call
... : 
    additional arguments, passed to plotting functions








Examples
--------

Same example as in dtw

>>> idx = seq(0,6_28,len=100);
>>> query = sin(idx)+runif(100)/10;
>>> reference = cos(idx)

>>> alignment = dtw(query,reference,keep=True);

>>> # A sample of the plot styles. See individual plotting functions for details

>>> plot(alignment, type="alignment",
>>>   main="DTW sine/cosine: simple alignment plot")

>>> plot(alignment, type="twoway",
>>>   main="DTW sine/cosine: dtwPlotTwoWay")

>>> plot(alignment, type="threeway",
>>>   main="DTW sine/cosine: dtwPlotThreeWay")

>>> plot(alignment, type="density",
>>>   main="DTW sine/cosine: dtwPlotDensity")




"""
        # ENDIMPORT
        dtwPlot(self, type, **kwargs)


# --------------------


def dtw(x, y=None,
        dist_method="euclidean",
        step_pattern="symmetric2",
        window_type=None,
        window_args={},
        keep_internals=False,
        distance_only=False,
        open_end=False,
        open_begin=False):
    # IMPORT_RDOCSTRING dtw
    """Dynamic Time Warp




Compute Dynamic Time Warp and find optimal alignment between two time
series.




**Details**

The function performs Dynamic Time Warp (DTW) and computes the optimal
alignment between two time series ``x`` and ``y``, given as numeric
vectors. The “optimal” alignment minimizes the sum of distances between
aligned elements. Lengths of ``x`` and ``y`` may differ.

The local distance between elements of ``x`` (query) and ``y``
(reference) can be computed in one of the following ways:

1. if ``dist_method`` is a string, ``x`` and ``y`` are passed to the
   [proxy::dist()] function in package :raw-latex:`\pkg{proxy}` with the
   method given;
2. if ``dist_method`` is a function of two arguments, it invoked
   repeatedly on all pairs ``x[i],y[j]`` to build the local cost matrix;
3. multivariate time series and arbitrary distance metrics can be
   handled by supplying a local-distance matrix. Element ``[i,j]`` of
   the local-distance matrix is understood as the distance between
   element ``x[i]`` and ``y[j]``. The distance matrix has therefore
   ``n=length(x)`` rows and ``m=length(y)`` columns (see note below).

Several common variants of the DTW recursion are supported via the
``step_pattern`` argument, which defaults to ``symmetric2``. Step
patterns are commonly used to *locally* constrain the slope of the
alignment function. See [stepPattern()] for details.

Windowing enforces a *global* constraint on the envelope of the warping
path. It is selected by passing a string or function to the
``window_type`` argument. Commonly used windows are (abbreviations
allowed):

-  ``"none"`` No windowing (default)
-  ``"sakoechiba"`` A band around main diagonal
-  ``"slantedband"`` A band around slanted diagonal
-  ``"itakura"`` So-called Itakura parallelogram

``window_type`` can also be an user-defined windowing function. See
[dtwWindowingFunctions()] for all available windowing functions, details
on user-defined windowing, and a discussion of the (mis)naming of the
“Itakura” parallelogram as a global constraint. Some windowing functions
may require parameters, such as the ``window_size`` argument.

Open-ended alignment, i_e. semi-unconstrained alignment, can be selected
via the ``open_end`` switch. Open-end DTW computes the alignment which
best matches all of the query with a *leading part* of the reference.
This is proposed e_g. by Mori (2006), Sakoe (1979) and others.
Similarly, open-begin is enabled via ``open_begin``; it makes sense when
``open_end`` is also enabled (subsequence finding). Subsequence
alignments are similar e_g. to UE2-1 algorithm by Rabiner (1978) and
others. Please find a review in Tormene et al. (2009).

If the warping function is not required, computation can be sped up
enabling the ``distance_only=True`` switch, which skips the backtracking
step. The output object will then lack the ``index{1,2,1s,2s}`` and
``stepsTaken`` fields.

``is_dtw`` tests whether the argument is of class ``dtw``.





Parameters
----------
x : 
    query vector *or* local cost matrix
y : 
    reference vector, unused if `x` given as cost matrix
dist_method : 
    pointwise (local) distance function to use. See
[proxy::dist()] in package \pkg{proxy}
step_pattern : 
    a stepPattern object describing the local warping steps
allowed with their cost (see [stepPattern()])
window_type : 
    windowing function. Character: "none", "itakura",
"sakoechiba", "slantedband", or a function (see details).
open_begin,open_end : 
    perform open-ended alignments
keep_internals : 
    preserve the cumulative cost matrix, inputs, and other
internal structures
distance_only : 
    only compute distance (no backtrack, faster)
d : 
    an arbitrary R object
... : 
    additional arguments, passed to `window.type`

Returns
-------

An object of class ``dtw`` with the following items:

-  ``distance`` the minimum global distance computed, *not* normalized.
-  ``normalizedDistance`` distance computed, *normalized* for path
   length, if normalization is known for chosen step pattern.
-  ``N,M`` query and reference length
-  ``call`` the function call that created the object
-  ``index1`` matched elements: indices in ``x``
-  ``index2`` corresponding mapped indices in ``y``
-  ``stepPattern`` the ``stepPattern`` object used for the computation
-  ``jmin`` last element of reference matched, if ``open_end=True``
-  ``directionMatrix`` if ``keep_internals=True``, the directions of
   steps that would be taken at each alignment pair (integers indexing
   production rules in the chosen step pattern)
-  ``stepsTaken`` the list of steps taken from the beginning to the end
   of the alignment (integers indexing chosen step pattern)
-  ``index1s, index2s`` same as ``index1/2``, excluding intermediate
   steps for multi-step patterns like [asymmetricP05()]
-  ``costMatrix`` if ``keep_internals=True``, the cumulative cost matrix
-  ``query, reference`` if ``keep_internals=True`` and passed as the
   ``x`` and ``y`` arguments, the query and reference timeseries.




Notes
-----

Cost matrices (both input and output) have query elements arranged
row-wise (first index), and reference elements column-wise (second
index). They print according to the usual convention, with indexes
increasing down- and rightwards. Many DTW papers and tutorials show
matrices according to plot-like conventions, i_e. reference index
growing upwards. This may be confusing.

A fast compiled version of the function is normally used. Should it be
unavailable, the interpreted equivalent will be used as a fall-back with
a warning.




References
----------

1. Toni Giorgino. *Computing and Visualizing Dynamic Time Warping
   Alignments in R: The dtw Package.* Journal of Statistical Software,
   31(7), 1-24. http://www_jstatsoft_org/v31/i07/
2. Tormene, P.; Giorgino, T.; Quaglini, S. & Stefanelli, M. *Matching
   incomplete time series with dynamic time warping: an algorithm and an
   application to post-stroke rehabilitation.* Artif Intell Med, 2009,
   45, 11-34. http://dx_doi_org/10_1016/j_artmed_2008_11_007
3. Sakoe, H.; Chiba, S., *Dynamic programming algorithm optimization for
   spoken word recognition,* Acoustics, Speech, and Signal Processing,
   IEEE Transactions on , vol_26, no_1, pp. 43-49, Feb 1978.
   http://ieeexplore_ieee_org/xpls/abs_all_jsp?arnumber=1163055
4. Mori, A.; Uchida, S.; Kurazume, R.; Taniguchi, R.; Hasegawa, T. &
   Sakoe, H. *Early Recognition and Prediction of Gestures* Proc. 18th
   International Conference on Pattern Recognition ICPR 2006, 2006, 3,
   560-563
5. Sakoe, H. *Two-level DP-matching–A dynamic programming-based pattern
   matching algorithm for connected word recognition* Acoustics, Speech,
   and Signal Processing, IEEE Transactions on, 1979, 27, 588-595
6. Rabiner L, Rosenberg A, Levinson S (1978). *Considerations in dynamic
   time warping algorithms for discrete word recognition.* IEEE Trans.
   Acoust., Speech, Signal Process., 26(6), 575-582. ISSN 0096-3518.
7. Muller M. *Dynamic Time Warping* in *Information Retrieval for Music
   and Motion*. Springer Berlin Heidelberg; 2007. p. 69-84.
   http://link_springer_com/chapter/10_1007/978-3-540-74048-3_4





Examples
--------


A noisy sine wave as query
>>> idx = seq(0,6_28,len=100);
>>> query = sin(idx)+runif(100)/10;

A cosine is for reference; sin and cos are offset by 25 samples
>>> reference = cos(idx)
>>> plot(reference); lines(query,col="blue");

Find the best match
>>> alignment = dtw(query,reference);


Display the mapping, AKA warping function - may be multiple-valued
Equivalent to: plot(alignment,type="alignment")
>>> plot(alignment$index1,alignment$index2,main="Warping function");

Confirm: 25 samples off-diagonal alignment
>>> lines(1:100-25,col="red")




Partial alignments are allowed.

>>> alignmentOBE  = 
>>>   dtw(query[44:88],reference,
>>>       keep=True,step=asymmetric,
>>>       open_end=True,open_begin=True);
>>> plot(alignmentOBE,type="two",off=1);


Subsetting allows warping and unwarping of
timeseries according to the warping curve. 
See first example below.

Most useful: plot the warped query along with reference 
>>> plot(reference)
>>> lines(query[alignment$index1]~alignment$index2,col="blue")

Plot the (unwarped) query and the inverse-warped reference
>>> plot(query,type="l",col="blue")
>>> points(reference[alignment$index2]~alignment$index1)



Contour plots of the cumulative cost matrix
similar to: plot(alignment,type="density") or
dtwPlotDensity(alignment)
See more plots in ?plot.dtw 

keep = TRUE so we can look into the cost matrix

>>> alignment = dtw(query,reference,keep=True);

>>> contour(alignment$costMatrix,col=terrain_colors(100),x=1:100,y=1:100,
>>> 	xlab="Query (noisy sine)",ylab="Reference (cosine)");

>>> lines(alignment$index1,alignment$index2,col="red",lwd=2);




An hand-checkable example

>>> ldist = matrix(1,nrow=6,ncol=6);  # Matrix of ones
>>> ldist[2,] = 0; ldist[,5] = 0;      # Mark a clear path of zeroes
>>> ldist[2,5] = .01;		 # Forcely cut the corner

>>> ds = dtw(ldist);			 # DTW with user-supplied local
>>>                                  #   cost matrix
>>> da = dtw(ldist,step=asymmetric);	 # Also compute the asymmetric 
>>> plot(ds$index1,ds$index2,pch=3); # Symmetric: alignment follows
>>>                                  #   the low-distance marked path
>>> points(da$index1,da$index2,col="red");  # Asymmetric: visiting
>>>                                         #   1 is required twice

>>> ds$distance;
>>> da$distance;







"""
    # ENDIMPORT

    if y is None:
        x = numpy.array(x)
        if len(x.shape) != 2:
            _error("A 2D local distance matrix was expected")
        lm = numpy.array(x)
    else:
        x = numpy.atleast_2d(x)
        y = numpy.atleast_2d(y)
        if x.shape[0] == 1:
            x = x.T
        if y.shape[0] == 1:
            y = y.T
        lm = cdist(x, y, metric=dist_method)

    wfun = _canonicalizeWindowFunction(window_type)

    step_pattern = _canonicalizeStepPattern(step_pattern)
    norm = step_pattern.hint

    n, m = lm.shape

    if open_begin:
        if norm != "N":
            _error(
                "Open-begin requires step patterns with 'N' normalization (e.g. asymmetric, or R-J types (c)). See Tormene et al.")
        lm = numpy.vstack([numpy.zeros((1, lm.shape[1])), lm])  # prepend null row
        np = n + 1
        precm = numpy.full_like(lm, numpy.nan, dtype=numpy.double)
        precm[0, :] = 0
    else:
        precm = None
        np = n

    gcm = _globalCostMatrix(lm,
                            step_pattern=step_pattern,
                            window_function=wfun,
                            seed=precm,
                            win_args=window_args)
    gcm = DTW(gcm)  # turn into an object, use dot to access properties

    gcm.N = n
    gcm.M = m

    gcm.openEnd = open_end
    gcm.openBegin = open_begin
    gcm.windowFunction = wfun
    gcm.windowArgs = window_args  # py

    # misnamed
    lastcol = gcm.costMatrix[-1,]

    if norm == "NA":
        pass
    elif norm == "N+M":
        lastcol = lastcol / (n + numpy.arange(m) + 1)
    elif norm == "N":
        lastcol = lastcol / n
    elif norm == "M":
        lastcol = lastcol / (1 + numpy.arange(m))

    gcm.jmin = m - 1

    if open_end:
        if norm == "NA":
            _error("Open-end alignments require normalizable step patterns")
        gcm.jmin = numpy.argmin(lastcol)

    gcm.distance = gcm.costMatrix[-1, gcm.jmin]

    if gcm.distance != gcm.distance:  # nan
        _error("No warping path found compatible with the local constraints")

    if step_pattern.hint != "NA":
        gcm.normalizedDistance = lastcol[gcm.jmin]
    else:
        gcm.normalizedDistance = numpy.nan

    if not distance_only:
        mapping = _backtrack(gcm)
        gcm.__dict__.update(mapping)

    if open_begin:
        gcm.index1 = gcm.index1[1:] - 1
        gcm.index1s = gcm.index1s[1:] - 1
        gcm.index2 = gcm.index2[1:]
        gcm.index2s = gcm.index2s[1:]
        lm = lm[1:, :]
        gcm.costMatrix = gcm.costMatrix[1:, :]
        gcm.directionMatrix = gcm.directionMatrix[1:, :]

    if not keep_internals:
        del gcm.costMatrix
        del gcm.directionMatrix
    else:
        gcm.localCostMatrix = lm
        if y is not None:
            gcm.query = x
            gcm.reference = y

    return gcm


# Return a callable object representing the window
def _canonicalizeWindowFunction(window_type):
    if callable(window_type):
        return window_type

    if window_type is None:
        return noWindow

    return {
        "none": noWindow,
        "sakoechiba": sakoeChibaWindow,
        "itakura": itakuraWindow,
        "slantedband": slantedBandWindow
    }.get(w, lambda: _error("Window function undefined"))


def _canonicalizeStepPattern(s):
    """Return object by string"""
    if isinstance(s, StepPattern):
        return s
    else:
        return getattr(sys.modules["dtwr.stepPattern"], s)


# Kludge because lambda: raise doesn't work
def _error(s):
    raise ValueError(s)
