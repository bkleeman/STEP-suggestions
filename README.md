# STEP (Storm Tracking and Evaluation Protocol)

STEP is a Python package that identifies, tracks, and computes physical characteristics of rainstorms given spatiotemporal precipitation data. The algorithms herein are implementations of those proposed by Chang et al. in [*Changes in Spatiotemporal Precipitation Patterns in Changing Climate Conditions*](https://geosci.uchicago.edu/~moyer/MoyerWebsite/Publications/Papers/Changes_Spatio-temporal_Precipitation_patterns.pdf), released by the [Center for Robust Decision-making on Climate and Energy Policy](https://www.rdcep.org). For implementation details, see the [wiki](https://github.com/bkleeman/STEP-suggestions/wiki).

## Summary
* [Installation](https://github.com/bkleeman/STEP-suggestions#installation)
* [Dependencies](https://github.com/bkleeman/STEP-suggestions#dependencies)
* [Usage](https://github.com/bkleeman/STEP-suggestions#usage)
* [Notes on Methodology](https://github.com/bkleeman/STEP-suggestions#notes-on-methodology)
* [Contributing](https://github.com/bkleeman/STEP-suggestions#contributing)
* [License](https://github.com/bkleeman/STEP-suggestions#license)

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
|[Basemap](https://matplotlib.org/basemap/)|1.2.1|
|[imageio](https://imageio.github.io)|2.8.0|
|[Matplotlib](https://matplotlib.org)|3.2.1|
|[netCDF4](https://unidata.github.io/netcdf4-python/netCDF4/index.html)|1.5.3|
|[NumPy](https://numpy.org)|1.18.5|
|[scikit-image](https://scikit-image.org)|0.17.2|
|[SciPy](https://scipy.org)|1.4.1|
|[six](https://github.com/benjaminp/six)|1.15.0|

## Usage

Please see `introduction.py`, for a comprehensive introduction to package use. See [Implementation Details](https://github.com/bkleeman/STEP-suggestions/wiki/Implementation-Details) for function signatures and usage tips. You can also call `help(`*`function`*`)` for information on these and functions called therein **<elaborate on this please -- do i call this within a python script? does it print to the console?>**. Depending on the function, calling `help()` will provide more info.

For a deeper introduction, see the [tutorial wiki](https://github.com/bkleeman/STEP-suggestions/wiki/Tutorial).

## Notes on Methodology

It is highly recommended that you review either the [methodology wiki](https://github.com/bkleeman/STEP-suggestions/wiki/Methodology) or the [original publication](https://geosci.uchicago.edu/~moyer/MoyerWebsite/Publications/Papers/Changes_Spatio-temporal_Precipitation_patterns.pdf) and its supplemental materials before use. Both the identification and tracking algorithms require highly sensitive user-specified parameters, and reviewing these materials -- particularly the "Usage Notes" associated with each algorithm **<okay but where are these??>**-- will help you achieve optimal results more quickly.

Please also see the associated paper for further information regarding reasoning behind these steps and the mathematics used herein. -- **<is this different from the original publication mentioned in the previous paragraph?>**

## Contributing

Changes are certainly welcome, as there are a good deal of complexity improvements to make on the implementation and functionality additions to build out related to the publication. If you would like to propose a change and/or note an error, please open an issue first to discuss what needs improvement (and, if applicable, how that might be accomplished).

### Future Work

Below are a list of generally useful ideas for future additions to STEP:

 - Adding the ability to use the computed metrics to find and visualize the spatial distribution of rainstorm characteristics, as covered in the publication.
 - Implementing a speed-up for the similarity measure computation. This could at least be done by dividing the calculation into subsets and summing their results.

## License
STEP is released under the [MIT License](https://choosealicense.com/licenses/mit/).

## Authors
* [Alex Rittler](Link_to_github_or_whatever_social_profile) - *lead developer*

## Acknowledgements
* [Won Chang](LinkedIn_or_RDCEP_profile_if_permission_given) - *research*
* [Michael Stein](LinkedIn_or_RDCEP_profile_if_permission_given) - *research*
* [Jiali Wang](LinkedIn_or_RDCEP_profile_if_permission_given) - *research*
* [Rao Kotamarthi](LinkedIn_or_RDCEP_profile_if_permission_given) - *research*
* [Elisabeth Moyer](LinkedIn_or_RDCEP_profile_if_permission_given) - *research*
* [Benjamin Kleeman](https://github.com/bkleeman) - *guidance on project structure and docs* 
