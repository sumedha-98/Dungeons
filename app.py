from flask import Flask, render_template, request
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import imageio
import os


app = Flask(__name__)

class DungeonGenerator:
    def __init__(self, width, height, num_rooms, max_room_width, min_room_width, max_room_height, min_room_height, overlap):
        random.seed(10) #introduces psuedo-randomness
        self.width = width
        self.height = height
        self.num_rooms = num_rooms
        self.max_room_width = max_room_width
        self.min_room_width = min_room_width
        self.max_room_height = max_room_height
        self.min_room_height = min_room_height
        self.overlap = overlap
        self.dungeon = np.zeros((height, width), dtype=int)    # Initialize with zeros
        

    def generate_dungeon(self):
        rooms = []
        frames = []  # List to store frames
        for _ in range(self.num_rooms):
            room_width = random.randint(self.min_room_width, self.max_room_width)  # Random room width between min room width and max_room_width
            room_height = random.randint(self.min_room_height, self.max_room_height)  # Random room height between min room height and max room height
            x = random.randint(0, self.width - room_width)  # Generate random x-coordinate
            y = random.randint(0, self.height - room_height)  # Generate random y-coordinate
            # Check if room overlaps with existing rooms
            if self.overlap == "no":
                if any(room_overlap(x, y, room_width, room_height, rx, ry, rw, rh) for rx, ry, rw, rh in rooms):
                    continue  # Skip this room if it overlaps
            # Create room in dungeon grid
            self.dungeon[y:y+room_height, x:x+room_width] = 1
            # Append current state of dungeon to frames
            frames.append(self.dungeon.copy())
            rooms.append((x, y, room_width, room_height))
        return frames

def room_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    """Check if two rooms overlap."""
    return (x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    width = int(request.form['user_input_width'])  # Width of the dungeon grid
    height = int(request.form['user_input_height'])  # Height of the dungeon grid
    num_rooms = int(request.form['user_input_num_rooms'])  # Number of rooms to generate
    max_room_width = int(request.form['user_input_max_width']) #maximum room width
    min_room_width = int(request.form['user_input_min_width']) #minimum room width
    max_room_height = int(request.form['user_input_max_height']) #maximum room height
    min_room_height = int(request.form['user_input_min_height']) #minimum room height
    overlap = request.form['yes_no'] #requirement of room overlap

    try:
        if max_room_width > width:
            raise ValueError("Max room width should be lesser than dungeon grid width")
        elif max_room_height > height:
            raise ValueError("Max room height should be lesser than dungeon grid height")
        elif width <= 0:
            raise ValueError("Width should be greater than 0")
        elif num_rooms <= 0:
            raise ValueError("Number of rooms should be greater than 0")
        elif max_room_width <= 0:
            raise ValueError("Max room width should be greater than 0")
        elif min_room_width <= 0:
            raise ValueError("Min room width should be greater than 0")
        elif max_room_height <= 0:
            raise ValueError("Max room height should be greater than 0")
        elif min_room_height <= 0:
            raise ValueError("Min room height should be greater than 0")
        elif height <= 0:
            raise ValueError("Height should be greater than 0")
        generator = DungeonGenerator(width, height, num_rooms, max_room_width, min_room_width, max_room_height, min_room_height, overlap)
    except ValueError as e:
        return str(e)
    frames = generator.generate_dungeon()
    gif_filename = 'dungeon_generation.gif'
    save_animation(frames, gif_filename)
    return render_template('result.html', gif_filename=gif_filename)

def save_animation(frames, gif_filename):
    if not os.path.exists('static'):
        os.makedirs('static')
    filenames = []
    for i, frame in enumerate(frames):
        filename = f'static/frame_{i}.png'
        plt.imsave(filename, frame, cmap='gray')
        filenames.append(filename)
    with imageio.get_writer(f'static/{gif_filename}', mode='I', duration=2.0) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
            os.remove(filename)  # Remove the temporary image files

if __name__ == '__main__':
    app.run(debug=True)
