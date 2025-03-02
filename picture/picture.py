import cv2
import numpy as np
import matplotlib.pyplot as plt

from qm import QuantumMachinesManager
from qm.qua import *
import math

################################################################################
# 1. IMAGE PROCESSING (OpenCV)
################################################################################

def resample_trace(x, y, points):
    """
    Resample the trace defined by x and y to a given number of points.
    """
    assert len(x) == len(y)
    t = np.linspace(0, len(x) - 1, points)
    x_resampled = np.interp(t, np.arange(len(x)), x)
    y_resampled = np.interp(t, np.arange(len(y)), y)
    return np.array([x_resampled, y_resampled])

# 1a) Load image and convert to grayscale
img = cv2.imread("face.jpg", cv2.IMREAD_GRAYSCALE)
if img is None:
    raise FileNotFoundError("Could not read 'face.jpg'. Make sure the file exists.")

# 1b) Detect edges with Canny (tweak thresholds as needed)
edges = cv2.Canny(img, 100, 200)

# 1c) Find contours
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if len(contours) == 0:
    raise ValueError("No contours found. Try adjusting Canny thresholds or using a simpler image.")

# 1d) Pick the largest contour by area
areas = [cv2.contourArea(cnt) for cnt in contours]
max_index = np.argmax(areas)
largest_contour = contours[max_index]

# 1e) Approximate the contour to reduce points (epsilon factor is adjustable)
epsilon = 0.001 * cv2.arcLength(largest_contour, True)
approx = cv2.approxPolyDP(largest_contour, epsilon, True)

# 1f) Extract (x, y) from the approximated contour
#    approx has shape (N, 1, 2)
pts = approx.reshape(-1, 2)  # shape (N, 2)
x_vals = pts[:, 0]
y_vals = pts[:, 1]

# 1g) Optional: invert Y or transform to a consistent orientation
#    For example, if you want "up" to be positive:
#    y_vals = -y_vals

# 1h) Normalize to ~±1 range
#    We find min/max, then scale and shift
min_x, max_x = x_vals.min(), x_vals.max()
min_y, max_y = y_vals.min(), y_vals.max()
range_x = max_x - min_x
range_y = max_y - min_y
# We'll scale the largest dimension to ~2.0, so the shape fits ~±1
scale_factor = 0.2 / max(range_x, range_y)
x_norm = (x_vals - min_x - range_x/2.0) * scale_factor
y_norm = (y_vals - min_y - range_y/2.0) * scale_factor

# 1i) Resample to a fixed number of points for QUA
resampled = resample_trace(x_norm, y_norm, points=16500)
face_x = resampled[0]
face_y = resampled[1]

# 1j) Let's visualize quickly (optional):
plt.figure()
plt.plot(face_x, face_y, '-o')
plt.title("Resampled Face Outline")
plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
plt.show()

################################################################################
# 2. BUILD QUA CONFIGURATION
################################################################################

SPRITE_LENGTH = 16500  # matches our resample_trace points

# We'll define waveforms for "face"
face_x_list = face_x.tolist()
face_y_list = face_y.tolist()

configuration = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1000",
            "fems": {
                5: {
                    "type": "LF",
                    "analog_outputs": {i: {"offset": 0.0} for i in range(1, 9)},
                    "analog_inputs": {},
                    "digital_outputs": {i: {} for i in range(1, 8)},
                }
            },
        }
    },
    "elements": {
        "screen": {
            "mixInputs": {
                "I": ("con1", 5, 5),
                "Q": ("con1", 5, 6),
            },
            "intermediate_frequency": 0,
            "operations": {
                "face": "face_pulse",
            },
        },
        'draw_marker_element': {
            'singleInput': {
                'port': ('con1', 5, 1),
            },
            'intermediate_frequency': 0,
            'operations': {
                "marker_pulse": "marker_pulse",
            },
        },
    },
    "pulses": {
        "face_pulse": {
            "operation": "control",
            "length": SPRITE_LENGTH,
            "waveforms": {"I": "face_x_wf", "Q": "face_y_wf"},
        },
        "marker_pulse": {
            "operation": "control",
            'length': SPRITE_LENGTH,
            'waveforms': {"single": "marker_wf"},
        },
    },
    "waveforms": {
        "face_x_wf": {
            "type": "arbitrary",
            "samples": face_x_list,
        },
        "face_y_wf": {
            "type": "arbitrary",
            "samples": face_y_list,
        },
        'marker_wf': {"type": "constant", "sample": 0.2},
    },
}

################################################################################
# 3. QUA PROGRAM TO DRAW THE FACE ON THE SCOPE
################################################################################

def move_cursor(x, y):
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)

def draw_face(x, y):
    move_cursor(x, y)
    play("face", "screen")

# We'll just do a minimal program that draws the face once, then loops or waits
qmm = QuantumMachinesManager("172.16.33.107",9510)

# Adjust IP/port as needed
qm = qmm.open_qm(configuration)

# A simple QUA program that draws the face at (0,0)
with program() as face_program:
    # If you want a loop, you can do a while_ or for_ loop. 
    # We'll just do one draw and then wait.

    # Draw the face at (0,0)
    draw_face_x = declare(fixed, value=0)
    draw_face_y = declare(fixed, value=0)

    # Actually draw
    
    with infinite_loop_():
        play("marker_pulse", "draw_marker_element")
        move_cursor(draw_face_x, draw_face_y)
        play("face", "screen")
    
    # Optionally wait a while to keep it on scope
    wait(1_000_000_00)  # e.g. 0.1 s in ns, or adjust as you like

# Execute
job = qm.execute(face_program)
print("Drawing face sprite on scope...")

# The program ends once that single wait is done. If you want it to hold,
# you can do a while_(True) loop in QUA or just re-run the program.

################################################################################
# 4. Optional Keyboard / Loop
################################################################################
# If you want to hold the shape indefinitely, consider a while_(True) in QUA
# or re-run the face program in a loop. For demonstration, we'll just leave it.
