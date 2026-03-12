import matplotlib.pyplot as plt

def single_plot(sequence_in, plot_title = "single_plot", plot_saved_name="", save_plot=False, show_plot=False,  show_axes = True):
    """Plots a single sequence with optional saving and display."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sequence_in)
    ax.set_title(plot_title)

    # Hide the axes according to user preference 
    if not show_axes :
        ax.get_xaxis().set_visible(False)
        # Hide the y-axis
        ax.get_yaxis().set_visible(False)

    if save_plot:
        if plot_saved_name:
            plt.savefig(plot_saved_name)
        else:
            print("Warning: save_plot is True but plot_saved_name is empty.")

    if show_plot:
        plt.show()
    plt.close(fig)

def double_plot(sequence_in_1, seq1_label, sequence_in_2, seq2_label, plot_title = "double_plots", plot_saved_name="", save_plot=False, show_plot=False,  show_axes = True):
    """Plots two sequences with labels, with optional saving and display."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sequence_in_1, label=seq1_label)
    ax.plot(sequence_in_2, marker='o', label=seq2_label)
    ax.set_title(plot_title)
    # ax.legend()

    # Hide the axes according to user preference 
    if not show_axes :
        ax.get_xaxis().set_visible(False)
        # Hide the y-axis
        ax.get_yaxis().set_visible(False)

    if save_plot:
        if plot_saved_name:
            plt.savefig(plot_saved_name)
        else:
            print("Warning: save_plot is True but plot_saved_name is empty.")

    if show_plot:
        plt.show()
    plt.close(fig)

def three_plot(sequence_in_1, seq1_label, sequence_in_2, seq2_label,sequence_in_3, seq3_label,  plot_title= "three plots", plot_saved_name="", save_plot=False, show_plot=False,  show_axes = True):
    """Plots three sequences with labels, with optional saving and display."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sequence_in_1, label=seq1_label)
    ax.plot(sequence_in_2, label=seq2_label)
    ax.plot(sequence_in_3, label=seq3_label)
    ax.set_title(plot_title)

    if not show_axes :
        # Hide the x-axis
        ax.get_xaxis().set_visible(False)
        # Hide the y-axis
        ax.get_yaxis().set_visible(False)
        
    # ax.legend()

    if save_plot:
        if plot_saved_name:
            plt.savefig(plot_saved_name)
        else:
            print("Warning: save_plot is True but plot_saved_name is empty.")

    if show_plot:
        plt.show()
    plt.close(fig)

def plot_coordinates(pixel_coordinates,x_label="x", y_label="y", plot_title= "coordiante plots", plot_saved_name="", save_plot=False, show_plot=False, show_axes = True):
    """Plots a coordiante pair the first argument, axis_1 being the x-axis values and axis_2 the y coordiante values. """

    print("Inside the plot_coordiantes function. ")

    axis_1 =  [i[0] for i in pixel_coordinates]
    x_label = "x"
    axis_2 = [i[1] for i in pixel_coordinates]
    y_label = "y"
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(axis_1, axis_2)
    
    if show_axes :
        ax.set_xlabel(xlabel=x_label)
        ax.set_ylabel(ylabel=y_label)
    else: 
        # Hide the x-axis
        ax.get_xaxis().set_visible(False)
        # Hide the y-axis
        ax.get_yaxis().set_visible(False)

    ax.set_title(plot_title)

    if save_plot:
        if plot_saved_name:
            plt.savefig(plot_saved_name)
        else:
            print("Warning: save_plot is True but plot_saved_name is empty.")

    if show_plot:
        plt.show()
    plt.close(fig)

def plot_ips_coordinates(ips_coordinate, flight_axis = "x_z", plot_title= "coordiante plots", plot_saved_name="", save_plot=False, show_plot=False, show_axes = True):
    """Plots IPS coordiante pair the first argument, axis_1 being the x-axis values and axis_2 the y coordiante values. """

    print("Inside the plot_ips_coordiantes function. ")

        
    if flight_axis == "y_z":
        axis1_index = 1
        x_label = "y-coordinates" 
        axis2_index = 2
        y_label ="z-coordinates"
    elif flight_axis == "x_y":
        axis1_index = 0
        x_label = "x-coordinates"
        axis2_index = 1
        y_label = "y-coordinates"
    else: 
        axis1_index = 0
        x_label = "x-coordinates"
        axis2_index = 2
        y_label = "z-coordinates"
    
    axis_1 =  [i[axis1_index] for i in ips_coordinate]
    axis_2 = [i[axis2_index] for i in ips_coordinate]
            
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(axis_1, axis_2)
    
    if show_axes :
        ax.set_xlabel(xlabel=x_label)
        ax.set_ylabel(ylabel=y_label)
    else: 
        # Hide the x-axis
        ax.get_xaxis().set_visible(False)
        # Hide the y-axis
        ax.get_yaxis().set_visible(False)

    ax.set_title(plot_title)

    if save_plot:
        if plot_saved_name:
            plt.savefig(plot_saved_name)
        else:
            print("Warning: save_plot is True but plot_saved_name is empty.")

    if show_plot:
        plt.show()
    plt.close(fig)
