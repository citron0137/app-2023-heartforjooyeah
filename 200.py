import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
from skimage import measure
import random

import matplotlib
#matplotlib.use('TkAgg')



min_shpere = 5
max_shpere = 30
x_max = 200
y_max = 50
z_max = 100
create_term = 3
screen_time = 100000

# Attaching 3D axis to the figure
fig = plt.figure()
#Put figure window on top of all other windows
#fig.canvas.manager.window.attributes('-topmost', 1)
#After placing figure window on top, allow other windows to be on top of it later
#fig.canvas.manager.window.attributes('-topmost', 0)

ax = p3.Axes3D(fig)


# Setting the axes properties
ax.view_init(0,90)
shape_list = []


def formula(x, y, z):
    return ((-y**2 * z**3 -9*x**2 * z**3/80) + (y**2 + 9*x**2/4 + z**2-1)**3)
    #return (x) ** 2 + (y) ** 2 + (z) ** 2 - 1**2

def update_shapes(num):
    if(num % create_term == 0 and screen_time - num > max_shpere*2):
        shape = {'startFrame':num, 'x_loc':random.randint(0,x_max),'y_loc':random.randint(0,y_max),'z_loc':random.randint(0,z_max)}
        shape_list.append(shape)
    
    #x_loc = 0
    #y_loc = 0
    #z_loc = 0
    

    ax.clear()
    for shape in shape_list:
        size = (num - shape['startFrame']) + min_shpere
        if(size > max_shpere):
            size = max_shpere*2 - size
        if(size < min_shpere):
            continue    
        x_loc = shape['x_loc']
        y_loc = shape['y_loc']
        z_loc = shape['z_loc']

        
        x = np.linspace(-2, 2, size) 
        y = np.linspace(-2, 2, size) 
        z = np.linspace(-2, 2, size) 
        X, Y, Z =  np.meshgrid(x, y, z)
        vol = formula(X,Y,Z) 
        verts, faces, normals, values = measure.marching_cubes(vol, 0,  spacing=(2, 2, 2))
        ax.plot_trisurf(verts[:, 0]+x_loc-size, verts[:,1]+y_loc-size, faces, verts[:, 2]+z_loc-size, cmap=cm.coolwarm, lw=0)


        
    ax.set_facecolor('black') 
    
    
    
    fig.set_facecolor('black')
    ax.grid(False) 
    ax.set_xlim3d([0.0, x_max])
    ax.set_ylim3d([0.0, y_max])
    ax.set_zlim3d([0.0, z_max])
    ax.set_box_aspect([x_max,y_max,z_max])
    ax.w_xaxis.pane.fill = False
    ax.w_yaxis.pane.fill = False
    ax.w_zaxis.pane.fill = False
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([]) 
    ax.get_zaxis().set_ticks([])   
    ax.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        
    return 

# Creating the Animation object

ani = animation.FuncAnimation(fig, update_shapes, screen_time, interval=10, blit=False)
plt.show()