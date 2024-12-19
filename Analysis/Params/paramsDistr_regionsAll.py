import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import torch
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from sympy import symbols, Eq, solve, sqrt, pi

# Adjust the path to include the project_root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sparch.models.snns import SNN
from sparch.models.snns import LIFcomplexLayer, adLIFclampLayer

dataset_name = "SHD"
batch_size = 128
nb_inputs = 700
nb_outputs = 20 if dataset_name == "shd" else 35
neuron_model = 'adLIFclamp'
nb_hiddens = 512
nb_layers = 3

layer_sizes = [nb_hiddens] * (nb_layers - 1) + [nb_outputs]
input_shape = (batch_size, None, nb_inputs)

extra_features = {
    'superspike': False,
    'slayer': False,
    'xavier_init': False,
    'no_reset': False,
    'half_reset': True,
    'rst_detach': False,
    'dt_min': 0.01,
    'dt_max': 0.4,
    's_GLU': False,
    'time_offset': 10,
    'thr': 1,
    'bRand': 'Rand',
    'c_discr': False,
    'c_param': False,
    'reset': 'half_reset'
}

net = SNN(
    input_shape=input_shape,
    layer_sizes=layer_sizes,
    neuron_type=neuron_model,
    dropout=0.1,
    normalization="batchnorm",
    use_bias=False,
    bidirectional=False,
    use_readout_layer=True,
    extra_features=extra_features
)

model_path = '../../exp/test_exps/shd_LIFcomplex_3lay512_drop0_1_batchnorm_nobias_udir_noreg_lr0_01/checkpoints/best_model.pth'
trained_net_cmplx = torch.load(model_path)
model_path = '../../exp/test_exps/shd_adLIFclamp_3lay512_drop0_1_batchnorm_nobias__/checkpoints/best_model.pth'
trained_net_adLIF = torch.load(model_path)
model_path = '../../SHD_runs/exp/paper_models/shd_ResonateFire_3lay512_/checkpoints/best_model.pth'
trained_net_rf = torch.load(model_path)

trained_net = torch.load(model_path)

def plot_eigenvalue_distribution():
    R = 1  # You may adjust this value for different systems
    tau_m_values = np.linspace(-0.1, 1.2, 10) 
    a_R_values = np.linspace(-1.2, 1.2, 10)
    
    ##tau_m_values = np.linspace(-5, 5, 100) 
    #a_R_values = np.linspace(-100, 100, 100)

    # Set up the plot
    plt.figure(figsize=(8, 6))
    plt.gca().add_patch(Rectangle((0.0196, -1), 1, 2, color='gray', alpha=0.7, zorder=2))

    for tau_m_over_tau_w in tau_m_values:
        for a_R in a_R_values:
            tau_m = 1  # Arbitrary tau_m value
            tau_w = tau_m / tau_m_over_tau_w
            a_w = a_R / R
            eigenvalues, _ = find_system_eigenvalues_numeric(tau_m, tau_w, R, a_w)
            
            # Compute the Nullstelle (1/tau_w)
            nullstelle = -1 / tau_w
            eigenvalues = [eigenvalues[0][0],eigenvalues[1][1]]
            if (eigenvalues[0]>0 and eigenvalues[0]!=nullstelle) or (eigenvalues[1]>0 and eigenvalues[1]!=nullstelle):
                plt.plot(tau_m_over_tau_w, a_R, color = "lightsalmon", alpha=0.2, zorder=1)
            # If eigenvalues are complex
            elif np.iscomplex(eigenvalues).any():
                plt.plot(tau_m_over_tau_w, a_R, color = "powderblue", alpha=0.2, zorder=1) # Blue dots for complex
            else:
                # Compare Nullstelle with min(eigenvalue)
                if nullstelle > eigenvalues[0] and nullstelle > eigenvalues[1]:
                    plt.plot(tau_m_over_tau_w, a_R, color = "peachpuff", alpha=0.2, zorder=1)  # Red dots if Nullstelle < min(eigenvalue)
                else:
                    plt.plot(tau_m_over_tau_w, a_R, color = "mistyrose", alpha=0.2, zorder=1) # Yellow dots if Nullstelle >= min(eigenvalue)

    # Create custom legend handles with correct colors
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', markersize=10, alpha=1, label='Oscillatory Dynamics'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, alpha=1, label='Non-oscillatory (Mixed) Dynamics'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='yellow', markersize=10, alpha=1, label='Non-oscillatory (integrator) Dynamics'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='green', markersize=10, alpha=1, label='Unstable'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=10, alpha=1, label='Neuron parameters after training'),
        Rectangle((0, 0), 1, 1, color='gray', alpha=0.9, label='Sparch AdLIF region')
    ]

    # Add legend
    plt.legend( handles=legend_elements)

    # Add labels and title
    

def find_system_eigenvalues_numeric(tau_m, tau_w, R, a_w):
    A = np.array([[-1/tau_m, -R/tau_m], [a_w/tau_w, -1/tau_w]])
    eigenvalues_matrix, eigenvectors = np.linalg.eig(A)
    eigenvalues = np.diag(eigenvalues_matrix)
    return eigenvalues, eigenvectors

def compute_alpha(log_log_alpha, alpha_img, log_dt):
    alpha = torch.exp((-torch.exp(log_log_alpha) + 1j * alpha_img) * torch.exp(log_dt))
    return alpha

def compute_rat_R_a(real_value, img_value, tau_m=0.01):
    rat, R_a = symbols('rat R_a')
    eq1 = Eq(-(rat + 1) / (2 * tau_m), real_value)
    eq2 = Eq(sqrt((rat**2 - 2*rat + 1 - 4*R_a * rat)*(-1)) / (2 * tau_m), img_value)
    solutions = solve([eq1, eq2], (rat, R_a))
    return solutions

tau_ratio_cmplx = [[], []] #np.zeros((2,512))
R_a_cmplx = [[], []] #np.zeros((2,512))

tau_ratio_adLIF = np.zeros((2,512))
R_a_adLIF = np.zeros((2,512))
tau_ratio_rf = np.zeros((2,512))
R_a_rf = np.zeros((2,512))

for i, trained_layer in enumerate(trained_net_cmplx.snn):
    
    if isinstance(trained_layer, LIFcomplexLayer):
        tau_m=0.01
        dt_orig = 0.001
        alpha_img = trained_layer.alpha_img.detach().cpu().numpy()
        log_dt = trained_layer.log_dt.detach().cpu().numpy()
        log_log_alpha = trained_layer.log_log_alpha.detach().cpu().numpy()
        dt = np.exp(log_dt)
        dt_factor = dt / dt_orig
        alpha_real = -np.exp(log_log_alpha)

        alpha = (-np.exp(log_log_alpha) + 1j * alpha_img) * dt_factor

        for alpha_val in alpha:
            real_value = alpha_val.real.item()
            img_value = alpha_val.imag.item()
            solutions = compute_rat_R_a(real_value, img_value, tau_m)

            for j, solution in enumerate(solutions):
                tau_ratio_cmplx[i].append(solution[0]) 
                R_a_cmplx[i].append(solution[1])
                #tau_ratio_cmplx[i, j] = solution[0]
                #R_a_cmplx[i, j] = solution[1]


for i, trained_layer in enumerate(trained_net_adLIF.snn):
    print(trained_layer)
    if isinstance(trained_layer, adLIFclampLayer):
        
        alpha = trained_layer.alpha.detach().cpu().numpy()
        beta = trained_layer.beta.detach().cpu().numpy()
        tau_ratio_adLIF[i,:] = np.log(beta)/np.log(alpha)
        R_a_adLIF[i,:] = trained_layer.a.detach().cpu().numpy()
        
for i in range(2):
    plot_eigenvalue_distribution()

    plt.scatter(tau_ratio_adLIF[i,:], R_a_adLIF[i,:], color='black', marker='o', s=1, alpha=1, zorder=3)
    plt.scatter(tau_ratio_cmplx[i], R_a_cmplx[i], color='blue', marker='o', s=1, alpha=1, zorder=3)
    #plt.xlim((-5,5))
    #plt.ylim((-100,100))
    plt.xlim((-0.1, 1.2))
    plt.ylim((-1.2, 1.2)) 
    plt.xlabel(' $\\tau_m / \\tau_w$')
    plt.ylabel('aR')
    plt.title(f'subthreshold parameters for layer {i}')
    plt.grid(True)

    plt.savefig(f"../../plots/SHD/Params/regions/All_rat_vs_R_a_layer{i}dtSmall.png")
    plt.show()
    plt.clf()  # Clear the figure for the next plot

