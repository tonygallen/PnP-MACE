from dotmap import DotMap
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

import pnp_mace as pnpm

"""
Load test image.
"""
img_path = "https://www.math.purdue.edu/~buzzard/software/cameraman_clean.jpg"
test_image = pnpm.load_img(img_path)  # create the image
image_data = np.asarray(test_image.convert("F")) / 255.0
ground_truth = Image.fromarray(image_data)

"""
Adjust ground truth image shape as needed to allow for up/down sampling.
"""
factor = 4  # Downsampling factor
new_size = factor * np.floor(ground_truth.size / np.double(factor))
new_size = new_size.astype(int)
ground_truth = ground_truth.crop((0, 0, new_size[0], new_size[1]))
resample = Image.NONE
clean_data = pnpm.downscale(ground_truth, factor, resample)

"""
Create noisy downsampled image.
"""
noise_std = 0.05  # Noise standard deviation
seed = 0          # Seed for pseudorandom noise realization
noisy_image = pnpm.add_noise(clean_data, noise_std, seed)

"""
Generate initial solution for MACE.
"""
init_image = pnpm.upscale(noisy_image, factor, Image.BICUBIC)

"""
Display test images.
"""
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(9, 9))
pnpm.display_image(ground_truth, title="Original", fig=fig, ax=ax[0, 0])
pnpm.display_image(clean_data, title="Downsampled", fig=fig, ax=ax[0, 1])
pnpm.display_image(noisy_image, title="Noisy downsampled", fig=fig,
                   ax=ax[1, 0])
pnpm.display_image_nrmse(init_image, ground_truth,
                         title="Bicubic reconstruction", fig=fig, ax=ax[1, 1])
fig.show()

"""
Set up the forward agent. We'll use a linear prox map, so we need to
define A and AT.
"""
downscale_type = Image.BICUBIC
upscale_type = Image.BICUBIC


def A(x):
    return np.asarray(pnpm.downscale(Image.fromarray(x), factor,
                                     downscale_type))


def AT(x):
    return np.asarray(pnpm.upscale(Image.fromarray(x), factor, upscale_type))


step_size = 0.1
forward_agent = pnpm.LinearProxForwardAgent(noisy_image, A, AT, step_size)

"""
Set up the prior agent.
"""
prior_agent_method = pnpm.bm3d_method

prior_params = DotMap()
prior_params.noise_std = step_size

prior_agent = pnpm.PriorAgent(prior_agent_method, prior_params)

"""
Compute and display one step of forward and prior agents.
"""
one_step_forward = forward_agent.step(np.asarray(init_image))
one_step_prior = prior_agent.step(np.asarray(init_image))

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(9, 5))
pnpm.display_image_nrmse(one_step_forward, ground_truth,
                         title="One step of forward model", fig=fig, ax=ax[0])
pnpm.display_image_nrmse(one_step_prior, ground_truth,
                         title="One step of prior model", fig=fig, ax=ax[1])
fig.show()

"""
Set up the equilibrium problem
"""
mu0 = 0.5  # Forward agent weight
mu = [mu0, 1 - mu0]
rho = 0.5
num_iters = 10
keep_all_images = False

equil_params = DotMap()
equil_params.mu = mu
equil_params.rho = rho
equil_params.num_iters = num_iters
equil_params.keep_all_images = keep_all_images

agents = [forward_agent, prior_agent]
equil_prob = pnpm.EquilibriumProblem(agents, pnpm.mann_iteration_mace,
                                     equil_params)

init_images = pnpm.stack_init_image(init_image, len(agents))

"""
Compute MACE iterations.
"""
final_images, residuals, vectors, all_images = equil_prob.solve(init_images)
v_sum = mu[0] * vectors[0] + mu[1] * vectors[1]
i0 = Image.fromarray(final_images[0])

"""
Display results.
"""
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(13.5, 5))
pnpm.display_image(ground_truth, title="Original", fig=fig, ax=ax[0])
pnpm.display_image_nrmse(init_image, ground_truth,
                         title="Bicubic reconstruction", fig=fig, ax=ax[1])
pnpm.display_image_nrmse(i0, ground_truth, title="MACE reconstruction",
                         fig=fig, ax=ax[2])
fig.show()


input()