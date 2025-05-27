import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import matplotlib.pyplot as plt
import numpy as np

from jaxfluids import InputManager, InitializationManager, SimulationManager
from jaxfluids_postprocess import load_data, create_2D_animation, create_2D_figure

# SETUP SIMULATION
input_manager = InputManager("risingbubble.json", "numerical_setup.json")
initialization_manager = InitializationManager(input_manager)
sim_manager = SimulationManager(input_manager)

# RUN SIMULATION
jxf_buffers = initialization_manager.initialization()
sim_manager.simulate(jxf_buffers)

# LOAD DATA
# path = "./results/risingbubble-15"
path = sim_manager.output_writer.save_path_domain
quantities = [
    "real_pressure", "real_density", "real_velocity",
    "levelset", "velocity", "volume_fraction", "density"]
jxf_data = load_data(path, quantities)

cell_centers = jxf_data.cell_centers
cell_sizes = jxf_data.cell_sizes
data = jxf_data.data
times = jxf_data.times

# PLOT
nrows_ncols = (1,4)
plot_dict = {
    "real_pressure": data["real_pressure"],
    "real_density" : data["real_density"],
    "velocityX": data["real_velocity"][:,0],
    "velocityY": data["real_velocity"][:,1],
}

image_path = "./images"
os.makedirs(image_path, exist_ok=True)
create_2D_animation(
    plot_dict,
    cell_centers,
    times,
    nrows_ncols=nrows_ncols,
    plane="xy", interval=100)

# CREATE FIGURE
create_2D_figure(
    plot_dict,
    nrows_ncols,
    cell_centers=cell_centers,
    plane="xy", plane_value=0.0,
    dpi=500,
    save_fig="rising_bubble.png")

# MASS
X, Y, Z = np.meshgrid(cell_centers[0], cell_centers[1], cell_centers[2], indexing="ij")
cell_volume = np.prod(np.array(cell_sizes))
volume_fraction = 1.0 - data["volume_fraction"]
density = data["density"][:,1]
velocity = data["velocity"][:,1,1]

cell_mass = volume_fraction * density * cell_volume
mass = np.sum(cell_mass, axis=(-3,-2,-1))
center_of_mass_x = np.sum(cell_mass * X, axis=(-1,-2,-3)) / mass
center_of_mass_y = np.sum(cell_mass * Y, axis=(-1,-2,-3)) / mass
rise_velocity = np.sum(cell_mass * velocity, axis=(-1,-2,-3)) / mass

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(10,3))
mass_exact = np.pi * 0.25**2 * 100
ax[0].plot(times, rise_velocity)
ax[1].plot(times, center_of_mass_y)
ax[2].plot(times, (mass - mass_exact)/mass_exact)
titles = ("rise velocity", "center of mass", "mass error")
for i, axi in enumerate(ax):
    axi.set_title(titles[i])
    axi.set_xlabel(r"$t$")
    axi.set_box_aspect(1.0)
plt.show()
plt.savefig("rising_bubble_metrics.png", bbox_inches="tight", dpi=200)
plt.close()
