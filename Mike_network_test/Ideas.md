# Thoughts on the project
## General thoughts on procedure, model, etc.

- There are two methods we thought of using. The first is to break the whole
($\varphi$, $N_w$, $\eta_{sp}$) space into discrete voxels, whose values are
either 0 (the surface does not go through the voxel) or 1 (it does). The 
second is to break only the domain ($\varphi$, $N_w$) space into pixels, whose 
values are the normalized $\eta_{sp}$ values. 
- After implementing the latter, we've noticed that our mean errors are 
massive, >100% for the third parameter. This has led me to believe that the 
former is the better option, as it better represents the classic ML case of 
finding an edge in an image.
- In determining the value of the voxels in the first case, we can simply
compute the values of $\eta_{sp}$ at the corner with the lower ($\varphi$, 
$N_w$) values and with the higher ($\varphi$, $N_w$) values, since $\eta_{sp}$ 
scales monotonically with both.
- By generating the surfaces directly on the GPU with torch, I can save time
in transferring the data across the bus, in addition to the raw speedup that
the GPU provides. With 32 CPU cores, I was generating, transferring, and 
learning the data at ~1M surfaces every 5 minutes at a resolution of (32, 32). 
With torch, I can do the same at around ~1M surfaces every 3-5 seconds.
- For the voxel method, we'll have to be careful about defining the edge
of the voxel vs. the center of the voxel.

## From discussion
1. Try Adam optimizer
2. Try loss functions (physics-based?)
3. Try Voxel method
4. Try transformers

## Web app

The web app logic should be as follows:

1. The user uploads data with a simple drag & drop of a csv/txt file containing
exactly three columns: concentration $\varphi=cl^3$, weight-average degree of
polymerization $N_w$ and specific viscosity $\eta_{sp}$. The user is 
responsible for calculating these values accurately, though we will provide an
explanation of $\varphi$ in the documentation.
2. Normalize the data to [0, 1] by taking the natural log and doing a simple 
linear transformation.
3. Apply the neural network.
4. Represent the data in four plots:
    - Concentration (original units) v. specific viscosity, with different
    markers/colors as different chain lengths (original units)
    - Concentration v. $\eta_{sp}/N_w \varphi^{1.31}$, with a line drawn for 
    the value of $B_g$. If no $B_g$, keep the plot, don't draw a line.
    - Concentration v. $\eta_{sp}/N_w \varphi^{2}$, with a line drawn for 
    the value of $B_{th}$. If no $B_{th}$, keep the plot, don't draw a line.
    - $N_w/g \lambda_g$ v. $\lambda \eta_{sp}$ with a curve drawn for the $P_e$
    crossover function (details to come). 
5. Display final parameters $\{B_g, B_{th}, P_e\}$, editable, and molecular
values Kuhn length $b$, excluded volume $v$, etc. Allow user to tweak 
parameters and refresh plots and values.
6. Button to create final report. Image files and data for plots, text file
(e.g., yaml, json, csv) for final parameters.
    - Anonymously log user data upon final report creation?