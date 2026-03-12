

import pygame
from src.translate_sketch_to_IPS import translate_sketch_to_ips
from src.read_save_sequences import read_tuple, save_sequences_to_file
from src.save_plots import double_plot, single_plot, plot_coordinates


def launch_flightmaker(mode_text=3, sketch_mode="sketch"):
    # import pygame
    # from translate_sketch_to_IPS import translate_sketch_to_ips
    # from Save_Read_Sequences import 

    pygame.init()
    WIDTH, HEIGHT = 1778, 1000 # 724, 320
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.image.load("lab_background.JPG")
    pygame.display.set_caption("Freehand Sketcher")

    # Setting background 
    if sketch_mode == "mission":
        background_image = pygame.image.load("lab_background.png").convert_alpha()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        background_image.set_alpha(200) # Example: 100 for partial opacity
    
    # else: 
        # print("Sketching challenge so no background image. ")


    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DRAW_COLOR = BLACK

    drawing = False
    last_pos = None
    all_strokes = []

    def save_sketch(strokes, filename):
        print("Inside the sketch saving function and printing the filename  is: ", filename)
        with open(filename, "w") as f:
            for stroke in strokes:
                for x, y in stroke:
                    if mode_text == 1:
                        f.write(f"{x/WIDTH}\n")
                    elif mode_text == 2:
                        f.write(f"{1-(y/HEIGHT)}\n")
                    elif mode_text == 3:
                        f.write(f"{x/WIDTH},{1-(y/HEIGHT)}\n")
                # f.write("STROKE_END\n")
        

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawing = True
                    current_stroke = []
                    all_strokes.append(current_stroke)
                    last_pos = event.pos
                    current_stroke.append(last_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
                    last_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    current_pos = event.pos
                    pygame.draw.line(screen, DRAW_COLOR, last_pos, current_pos, 2)
                    last_pos = current_pos
                    all_strokes[-1].append(current_pos)

        screen.fill(WHITE)
        if sketch_mode == "mission":
            screen.blit(background_image, (0,0))   # added in October to use background image 
        # else: 
            # print("Sketching challenge so no background image. ")

        for stroke in all_strokes:
            if len(stroke) > 1:
                pygame.draw.lines(screen, DRAW_COLOR, False, stroke, 3)
        pygame.display.flip()

    # ----------       Pixel coordinates            ------------------------- 

    # saving all sketches 
    save_sketch(all_strokes, filename=f"challenge_sketch.txt")  # {sketch_mode}
    all_stroke_points = read_tuple(f"challenge_sketch.txt")  # {sketch_mode}
    # Sampling points in the pixel domain of translated coordinates 
    sampled_pixel_points = []
    for index, value in enumerate(all_stroke_points):
        if (index%8 ==0):
            sampled_pixel_points.append(value)  
    
    # -----------        IPS coordiantes         -------------------------------------
    translated_coordinates, translated_sampled_coordinates = translate_sketch_to_ips(all_stroke_points)
    save_sequences_to_file(translated_coordinates, f"{sketch_mode}_all_IPS_coordinates.txt")
    save_sequences_to_file(translated_sampled_coordinates, f"sampled_IPS_{sketch_mode}.txt")


    print("Before saving the coordinates. ")
    save_sequences_to_file(sampled_pixel_points, "sampled_pixel_coordinates.txt")  #
    
    # double_plot(all_stroke_points)
    # Plotting the sketched pattern : 
        # Extracting tuple/coordiantes into 1D sequences 
    x_coordinate = [i[0] for i in all_stroke_points]
    y_coordinate = [i[1] for i in all_stroke_points]

    # Saving plot sequence as an image
    plot_coordinates(all_stroke_points,  save_plot=True, plot_saved_name=f"{sketch_mode}_plot.png", plot_title="", show_axes=False)

    pygame.quit()
    return f"{sketch_mode}_sketch.txt" , sampled_pixel_points  # translated_sampled_coordinates  # "{sketch_mode}_sketch.txt"

if __name__ == "__main__":
    launch_flightmaker()