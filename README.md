# STEP (Storm Tracking and Evaluation Protocol)

STEP is a Python package that identifies, tracks, and computes physical characteristics of rainstorms given spatiotemporal precipitation data. The algorithms herein are implementations of those proposed by Chang et al. in [*Changes in Spatiotemporal Precipitation Patterns in Changing Climate Conditions*](https://geosci.uchicago.edu/~moyer/MoyerWebsite/Publications/Papers/Changes_Spatio-temporal_Precipitation_patterns.pdf), released by the [Center for Robust Decision-making on Climate and Energy Policy](https://www.rdcep.org). For implementation details, see the [wiki](https://github.com/bkleeman/STEP-suggestions/wiki).

## Installation

 To install STEP, ensure that you are using Python 3.7.4 **(or whatever version)** and use the package manager [pip](https://pip.pypa.io/en/stable/).

```bash
pip install STEP
cd STEP
<further instructions here>
```

## Dependencies
|Name|Version|
|--|--|
|[Basemap](matplotlib.org/basemap)|1.2.1|
|[imageio](imageio.github.io)|2.8.0|
|[Matplotlib](matplotlib.org)|3.2.1|
|[netCDF4](unidata.github.io/netcdf4-python/netCDF4/index.html)|1.5.3|
|[NumPy](numpy.org)|1.18.5|
|[scikit-image](scikit-image.org)|0.17.2|
|[SciPy](scipy.org)|1.4.1|
|[six](https://github.com/benjaminp/six)|1.15.0|

## Usage

Please see `introduction.py`, which provides a comprehensive introduction to package use. For further specificity, see the function signatures and usage tips for the main functionality listed below or call `help(`*`function`*`)` for information on these and functions called therein. Depending on the function, the latter may provide more function-specific information.

## Methodology

*Note:* It is highly recommended to review this methodology or that which is available in the original publication and the accompanying supplemental materials before use. Since both the identification and tracking algorithms require user-specified parameters and are quite sensitive to these, reviewing this material, especially the "Usage Notes" accompanying each algorithm, will likely reduce time spent tuning for optimal results.

Please also see the associated paper for further information regarding reasoning behind these steps and the mathematics used herein.

UPDATE

### Identification

Identification of individual storms within each time slice is computed as follows in both high-level overview form and an implementation outline that closely follows the numbered steps in the code released to aid in understanding. Following these are some quick tips compiled for ease of use when getting started with the algorithm and making sense of its results!

#### Algorithm Overview

 1. Find all contiguous precipitation regions. That is, perform (fully) connected-component labeling.
 2. Classify a storm region as large if it has one or more remaining grid cells left after an erosion operation and small otherwise.
 3. For regions in the set of large regions:
     1. Find smoothed regions using an opening operation.
     2. Perform almost-connected-component labeling on them.
     3. Group the large regions based on the clustering results.
 4. For regions in the set of small regions:
	 1. Dilate each region.
	 2. If any larger regions overlap, add the region to the cluster that shares the largest number of grid cells.
	 3. Otherwise, perform almost-connected-component labeling for the regions not added to any clusters for the large regions.

### Tracking

Once the rainstorm segments for all time slices are identified, we link them through consecutive time steps to form rainstorm events evolving over time. The tracking of storm events is computed as follows, once again in both high-level overview form and an implementation outline that closely follows the numbered steps in the code released.

CHANGE TO FOLLOWS COMMENTS PROVIDED IN PACKAGE

#### Algorithm Overview

 1. At *t=0*, assign the rainstorm segments to different rainstorm events as their starting segments.
 2. For *t=1* onwards:
	 1. Link each segment to one of the segments in the previous step based on *similarity measure* and magnitude of *displacement vector*. More specifically, link the two if the following conditions are satisfied:
		 1. The shape of the two events are similar enough so that the value of the *similarity measure* between them exceeds a *tau* threshold of 0.05 in summer and 0.01 in winter **and**
		 2. The link does not result in too drastic a change of storm location in the opposite direction to its original movement. That is, we allow linkage only when the magnitude of the *displacement vector* of the two segments is less than (the equivalent of) 120 km (in grid cells) regardless of direction, **or** the angle between the *displacement vector* and the displacement between the segment in the previous time slice and its predecessor is less than 120 degrees.
	2. If no events satisfy the criteria, let the segment initialize a new rainstorm event as its starting segment.

#### Similarity Measure Overview

The implementation of the similarity measure calculation is a very technical and largely unintuitive one. For this reason, please also see the extensive comments provided in `tracking.py`. As is suggested there, working through a small example will likely be very helpful in understanding not only the specific implementation, but the idea behind it as well.

***

Due to the nature of the double summation, a vectorized solution is crucial here, though enormously memory heavy. Thus, in order to minimize this issue while maintaining some speed, the *similarity measure* is computed involving the union of cell locations in the two storms, since overlapping cells have no effect on similarity. This of course will lead to greater memory usage when there is no overlap, but has had a significantly positive effective when there is some and storms are very large, since this is where computation is normally derailed with a more straightforward implementation. 

 1. For each of the two storms, compute the relative weight for each grid cell, preserving the shape of the array.
 2. Again for each, find the coordinates of the non-zero precipitation data corresponding to each storm and compute their union, as overlapping cells will not effect our result.
 3. Reshape the location arrays into 1d arrays and compute their union.
 4. Place these coordinates in identical 1d arrays.
 5. Create two new arrays of weights, where each weight is added to the array only if its coordinates exist in the union of coordinates and placed where those coordinates exist the union of coordinates.
 6. Reshape both arrays of weights into 1d arrays, one as a column and one as a row, and compute their matrix multiplication.
 7. Similarly, compute the distances between each pair of coordinates in the coordinate arrays. 
 *(We now have two arrays where the distance between each relevant cell pairing of the two storms in the array of multiplied, relative weights can be found at the same location in the distance array.)*
 8. Compute the exponential involving *phi* element-wise on the array of distances.
 9. Compute the element-wise multiplication of this resulting array with the array of multiplied, relative weights.
 10. The summation of this array gives the *similarity measure* of the two storms.

CHANGE AND ADD HIGH LEVEL OVERVIEW
 
### Physical Characteristics
 
 Once rainstorm events have been tracked through time, we are able to characterize each individual rainstorm event with four metrics: duration, size, mean intensity, and central location. These are computed as follows.
 
#### Algorithm Overviews (and Code Outlines)
No explicit code outlines are given for this section, since the overviews virtually act as such. For more information on the implementation, see `quantification.py`.
##### Duration
 - Create a new dictionary.
 - Find all the storms in the tracked storm data.
 - Create a new array of length equal to the number of storms found. 
 - For each time slice:
	 1. Compute the storms that appear in that time slice.
	 2. For each storms in the set of all storms:
		 1. If that storm is in the set of storms that appear in this time slice:
			 1. If the storm is not already in the dictionary, add it with value 1.
			 2. Otherwise, increment the value found at the key equal to that storm.
 - For each key, value pair in the dictionary:
	1. If the key isn't the background:
		1. Set the value found at [*key*] of the array to the key's value in the dictionary.
 - Multiply each value of the array to be returned by the time interval. 
##### Size
 - Create an array with dimensions *number of time slices **x** number of storms*.
 - For each time slice:
	1. Find the storms that appear in it.
	2. For each storm that appears in this time slice:
		1. Compute the number of grid cells belonging to it.
		2. Place this result at the corresponding [*time*][*storm*] location in the array.
 - Multiply the number of grid cells by the specified grid cell size for the data.
##### Average intensity
 - Create an array with dimensions *number of time slices **x** number of storms*.
 - For each time slice:
	1. Find the storms that appear in it.
	2.  For each storm that appears in this time slice:
		1. Find and sum the precipitation belonging to the storm in the current time slice.
		2. Find the storm's average precipitation in this time slice.
		3.  Place this result at the corresponding [*time*][*storm*] location in the array.
##### Central location
 1. Create an array with dimensions *number of time slices **x** number of storms* to store the results of our computations, but of type object to allow us to store an array in each cell.
 2. Create arrays of x, y, and z values corresponding to the latitude and longitude data converted into the Cartesian grid in R<sup>3</sup>.
 3. For each time slice:
	1.  Find the storms that appear in it.
	2.  For each storm that appears in this time slice:
		1. Find the sum of the precipitation values belonging to the storm.
		2. Compute the intensity weighted averages corresponding to the grid in R<sup>3</sup> for the storm.
		3. Find the nearest point on Earth's surface.
		4. Place this result at the corresponding [*time*][*storm*] location in the array.

## Contributing

Changes are certainly welcome, as there are a good deal of complexity improvements to make on the implementation and functionality additions to build out related to the publication. If you would like to propose a change and/or note an error, please open an issue first to discuss what needs improvement (and, if applicable, how that might be accomplished).

### Future Work

Below are a list of generally useful ideas for future additions to STEP:

 - Adding the ability to use the computed metrics to find and visualize the spatial distribution of rainstorm characteristics, as covered in the publication.
 - Implementing a speed-up for the similarity measure computation. This could at least be done by dividing the calculation into subsets and summing their results.

## License
STEP is released under the [MIT License](https://choosealicense.com/licenses/mit/).
