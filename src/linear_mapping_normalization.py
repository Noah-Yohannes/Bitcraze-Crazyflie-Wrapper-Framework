
def normalize_value(value, current_min, current_max, desired_minimum, desired_maximum):
    """A function that linearly maps a value to a range specified by a minimum and maximum values. This function should be added to the Normalization_script. """

    normalized_value = (((value-current_min)*(desired_maximum-desired_minimum))/(current_max-current_min)) + desired_minimum

    if normalized_value > desired_maximum:
        normalized_value = desired_maximum
    if normalized_value < desired_minimum:
        normalized_value = desired_minimum
    return normalized_value