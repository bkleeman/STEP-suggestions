import copy
import numpy as np
from scipy.ndimage.measurements import label
from scipy.ndimage.morphology import generate_binary_structure
from skimage import morphology
from skimage.segmentation import relabel_sequential


def identify(data: np.ndarray, morph_structure: np.ndarray) -> np.ndarray:
    """Divides the precipitation field at each time step into individual storms using morphological operations
    and connected-component labeling.
    :param data: the precipitation data, given as an array of dimensions Time x Rows x Cols. To identify
    storms in a single time slice, reshape the array to dimensions (1, Rows, Cols).
    :param morph_structure: the structural set used to perform morphological operations, given as an array. See
    scipy.morphology for more information.
    :return: an array of time slice maps with individual storms labeled at each time slice, with the dimensions of
    data.
    """

    # 1) Run connected-components algorithm on all time slices:

    # find the dimensions of the input
    shape = data.shape
    num_time_slices, row, col = shape

    # initialize a new empty array of these dimensions to hold the result of running the connected-components algorithm
    # on all time slices
    label_array = np.empty((num_time_slices, row, col)).astype(int)

    # use 8-connectivity for determining connectedness below
    connectivity = generate_binary_structure(2, 2)

    # run the connected-components algorithm on the data and store it in our new array
    # since we will repeat this process often, we use a higher order function to compute the desired result
    perform_connected_components(data, label_array, num_time_slices, connectivity)

    # 2) Run erosion on labeled maps:

    # initialize an array of the same dimensions to store morphological transformations in
    morphology_array = np.zeros((num_time_slices, row, col)).astype(int)

    # perform the necessary erosion operation using a similar higher order function
    # note: here we make use of our defined structural set given as input
    perform_morph_op(morphology.erosion, label_array, morphology_array, num_time_slices, morph_structure)

    # 3) Classify storms with 1 or more remaining grid cells after erosion as large:

    # initialize a list of sets, where the list's indices correspond to time slices of the dataset
    large_storms = [set() for _ in range(num_time_slices)]

    # for each time slice, if the slice originally had any labeled storms
    for time_index in range(num_time_slices):
        num_labels = np.max(label_array[time_index])
        # for each of these labels, check if the label still appears after the erosion
        for storm_segment in range(1, num_labels + 1):
            if storm_segment in morphology_array[time_index]:
                # if so, add it to the set of large storms for the current time slice
                large_storms[time_index].add(storm_segment)

    # 4) For the set of large storms, find smoothed regions using an opening operation:

    # initialize an array of the same dimensions as the others
    large_storm_array = np.zeros((num_time_slices, row, col)).astype(int)

    # write in the large storm labels at their appropriate locations
    for time_index in range(num_time_slices):
        for col_index in range(col):
            for row_index in range(row):
                if label_array[time_index][row_index][col_index] in large_storms[time_index]:
                    large_storm_array[time_index][row_index][col_index] = \
                        label_array[time_index][row_index][col_index]

    # define the array of small storms as the array holding the initial connected-components without those found to be
    # large storms
    small_storm_array = np.where(large_storm_array != 0, 0, label_array)

    # reuse our morphology array for another morphological operation, this time 'opening', to produce our desired
    # smoothed storm regions
    perform_morph_op(morphology.erosion, large_storm_array, morphology_array, num_time_slices, morph_structure)
    perform_morph_op(morphology.dilation, morphology_array, morphology_array, num_time_slices, morph_structure)

    # 5) Perform almost-connected-component labeling on the large storms:

    # dilate newly-smoothed regions
    perform_morph_op(morphology.dilation, morphology_array, morphology_array, num_time_slices, morph_structure)

    # run fully-connected-components algorithm on them
    perform_connected_components(morphology_array, morphology_array, num_time_slices, connectivity)

    # map clustering results onto array of large storms, but only where the storms exist in the original data
    for time_index in range(num_time_slices):
        for storm in np.unique(morphology_array[time_index]):
            if storm:
                overlap = np.where((large_storm_array[time_index] != 0) & (morphology_array[time_index] == storm),
                                   1, 0).astype(int)
                if np.max(overlap) > 0:
                    labels = np.unique(np.where(overlap == 1, large_storm_array[time_index], 0))
                    large_storm_array[time_index] = np.where(np.isin(large_storm_array[time_index], labels) &
                                                             (large_storm_array[time_index] != 0),
                                                             storm + np.max(label_array), large_storm_array[time_index])

    # 6) Add small areas to existing nearby rainstorm events:

    # copy the large storm array to compute overlaps against, ensuring overlaps are calculated on the same large storm
    # array data each time
    large_copy = copy.deepcopy(large_storm_array)

    # perform almost connected-component labeling on the small storm array
    # small_dilated = np.empty((num_time_slices, row, col)).astype(int)
    perform_morph_op(morphology.dilation, small_storm_array, morphology_array, num_time_slices, morph_structure)
    perform_connected_components(morphology_array, morphology_array, num_time_slices, connectivity)
    for time_index in range(num_time_slices):
        small_storm_array[time_index] = np.where(small_storm_array[time_index] != 0, morphology_array[time_index],
                                                 small_storm_array[time_index])

    # find unique labels at each time slice for both large and small storm arrays
    for time_index in range(num_time_slices):
        # find the unique labels at each time slice for both large and small storm arrays
        unique_elements_large = np.unique(large_storm_array[time_index])
        unique_elements_small = np.unique(small_storm_array[time_index])

        # for each small storm cluster
        for small_index, small_storm in enumerate(unique_elements_small):
            max_cells_overlap = 0  # max overlap between a small storm and all large storms at that time slice
            overlap_amount = 0  # count for any particular combination (maximal or not)
            if small_storm == 0:
                continue
            # for each large storm
            for large_index, large_storm in enumerate(unique_elements_large):
                if large_storm == 0:
                    continue
                # find where the two storms overlap
                overlap_amount = np.sum(np.where((large_copy[time_index] == large_storm) &
                                                 (morphology_array[time_index] == small_storm), 1, 0))
                # if we've found a larger overlap
                if overlap_amount > max_cells_overlap:
                    # save the label of the overlapping large storm and update the maximum overlap
                    largest_overlap_label = large_storm
                    max_cells_overlap = overlap_amount
            # if we've found any overlaps
            if max_cells_overlap and largest_overlap_label:
                # write the small storm into the (original) large storm array using the label of the cluster with
                # maximum overlap, but only at the locations where it appears in the un-dilated small storm array
                large_storm_array[time_index] = np.where(small_storm_array[time_index] == small_storm,
                                                         largest_overlap_label, large_storm_array[time_index])
                # remove this small storm from the small storm array
                small_storm_array[time_index] = np.where(small_storm_array[time_index] == small_storm, 0,
                                                         small_storm_array[time_index])

    # 7) Find rainstorm events consisting only of small areas:

    # perform almost-connected-component labeling on those small storms that are left
    perform_morph_op(morphology.dilation, small_storm_array, morphology_array, num_time_slices, morph_structure)
    perform_connected_components(morphology_array, morphology_array, num_time_slices, connectivity)

    # store the max label used in each time slice of the large storm array
    largest_storm_label = np.empty((num_time_slices, 1, 1)).astype(int)

    # take the results of our almost-connected-component labeling on the small storms and add the
    # largest label in that time slice to it in order to produce a new label to add to the large storm array in the same
    # location there
    for time_index in range(num_time_slices):
        largest_storm_label[time_index] = np.max(large_storm_array[time_index])

    large_storm_array = np.where((small_storm_array != 0), morphology_array +
                                 largest_storm_label, large_storm_array)

    result = np.empty_like(large_storm_array)

    # 8) Relabel the labels in each time slice sequentially from 1:
    for time_index in range(num_time_slices):
        result[time_index] = relabel_sequential(large_storm_array[time_index])[0]

    return result


def perform_connected_components(to_be_connected: np.ndarray, result: np.ndarray, lifetime: int,
                                 connectivity_type: np.ndarray) -> None:
    """Higher order function used to label connected-components on all time slices of a dataset.
    :param to_be_connected: the data to perform the operation on, given as an array of dimensions Time x Rows x Cols.
    :param result: where the result of the operation will be stored, with the same dimensions as to_be_connected.
    :param lifetime: the number of time slices in the data, given as an integer.
    :param connectivity_type: an array representing the type of connectivity to be used by the labeling algorithm. See
    scipy.ndimage.measurements.label for more information.
    :return: (None - the operation is performed on the result in place.)
    """
    for index in range(lifetime):
        cc_output, _ = label(to_be_connected[index], connectivity_type)  # label also returns # of labels found
        result[index] = cc_output


def perform_morph_op(morph_function: object, to_be_morphed: np.ndarray,
                     result: np.ndarray, lifetime: int, structure: np.ndarray) -> None:
    """Higher order function used to perform a morphological operation on all time slices of a dataset.
    :param morph_function: the morphological operation to perform, given as an object (function).
    :param to_be_morphed: the data to perform the operation on, given as an array of dimensions Time x Rows x Cols.
    :param result: where the result of the operation will be store, with the same dimensions as to_be_morphed.
    :param lifetime: the number of time slices in the data, given as an integer.
    :param structure: the structural set used to perform the operation, given as an array. See scipy.morphology for more
    information.
    :return: (None - the operation is performed on the result in place.)
    """
    for index in range(lifetime):
        operation = morph_function(to_be_morphed[index], structure)
        result[index] = operation
