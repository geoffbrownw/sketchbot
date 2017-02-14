#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      GeoffB
#
# Created:     31/12/2014
# Copyright:   (c) GeoffB 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

import math

def get_median_absolute_deviation(sample_list):

    """Calculate variance measure that is robust against outliers"""

    sample_size = len(sample_list)
    median_index = int(sample_size/float(2))
    sample_list = sorted(sample_list)
    median = sample_list[median_index]
    absolute_deviations = [abs(sample - median) for sample in sample_list]

    absolute_deviations = sorted(absolute_deviations)
    median_of_absolutes = absolute_deviations[median_index]

    return median_of_absolutes


def create_frequency_histogram(sample_list, bucket=0):

    """ I want to bucket each occurence for a line the threshold will
    be +/- 180. To bucket non-line testing samples this really onlye
    works on 0-50 or so and only in the smallest to largest order
    sort by the bucket"""

    # sample size may not consume all the possibilities

    sample_size = len(sample_list)
    bucket_list = []

    for threshold in range(0, sample_size, 5):
        bucket = [sample for sample in sample_list
                  if threshold <= sample <= threshold + 5]
        if bucket:
            bucket_size = len(bucket)
            bucket_list.append(bucket_size)
        else:
            bucket_list.append(0)

    return bucket_list


def calc_variance(cross_list, pop_or_samp=0):

    """Calculate statictical variance from a set of integers representing
    the angle of a pixel"""

    dif_list = []
    difsqr_list = []
    cross_sum = sum(cross_list)
    cross_len = len(cross_list)

    if cross_len > 0:
        cross_avg = cross_sum/float(cross_len)
        dif_list = [cross - cross_avg for cross in cross_list]
        difsqr_list = [diff**2 for diff in dif_list]

        if pop_or_samp == 0: #population
            sum_sqr = sum(difsqr_list)/float(cross_len)
        else: # sample
            sum_sqr = sum(difsqr_list)/float(cross_len - 1)
        variance = round(math.sqrt(sum_sqr), 3)
    else:
        variance = .5
    return variance


if __name__ == '__main__':
    main()
