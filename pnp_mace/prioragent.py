from agent import *

# prox_tv denoiser:  https://pythonhosted.org/prox_tv/
import prox_tv as ptv
from bm3d import bm3d

# TODO:
# Additional denoisers:
#   https://scikit-image.org/docs/dev/auto_examples/filters/plot_denoise_wavelet.html
#   https://scikit-learn.org/stable/auto_examples/decomposition/plot_image_denoising.html
#   NN?

# This file contains the class declaration for PriorAgent as well as particular
# prior agent methods.


class PriorAgent(Agent):
    """
    Class to provide a container and interface to various prior models.
    """

    def __init__(self, prior_agent_method, params):
        """
        Define the basic elements of the prior agent: the data to fit and the method
        used to update the input to reflect the data.

        Args:
            prior_agent_method: method to update input to reflect data
            params: parameters used by the prior agent method
        """
        super().__init__()
        self.method = prior_agent_method
        self.params = params

    def step(self, agent_input):
        """
        Apply the update method one time

        Args:
            agent_input: The current reconstruction

        Returns:
            The reconstruction after one application of the prior method
        """
        return self.method(agent_input, self.params)

######################
# Particular prior agent methods


def tv1_2d(agent_input, params):
    """
    Proximal map for L1 total variation

    Args:
        agent_input: full-size reconstruction
        params:  params.noise_std for noise standard deviation

    Returns:
        New full-size reconstruction after update
    """
    noise_var = params.noise_std**2
    return ptv.tv1_2d(agent_input, noise_var)


def tv2_2d(agent_input, params):
    """
    Proximal map for L2 total variation

    Args:
        agent_input: full-size reconstruction
        params:  params.noise_std for noise standard deviation

    Returns:
        New full-size reconstruction after update
    """
    noise_var = params.noise_std**2
    return ptv.tvp_2d(agent_input, noise_var, noise_var, 2, 2)


def bm3d_agent(agent_input, params):
    """
    BM3D agent

    Args:
        agent_input: full-size reconstruction
        params:  params.noise_std for noise standard deviation

    Returns:
        New full-size reconstruction after update
    """

    return bm3d(agent_input, params.noise_std)