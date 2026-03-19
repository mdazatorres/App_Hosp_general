import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

"""
This file is just for verify that the implemantions to streamlit give the same results
than our initial functions.

As we have to trasform this function to work in a modular way , We want to be sure
that suech implementation is done propertialy.
This function for now it is used in surge_analysis.oy
"""

def compute_equilibrium_data(fixed_params, arrivals_mean, Ad_Hs_mean, Ad_Hm_mean, Ad_ICU_mean,
                             At_Hs_mean, At_Hm_mean, At_ICU_mean):
    sigma = fixed_params['sigma']
    omega = fixed_params['omega']
    pED_Hs = fixed_params['pED_Hs']
    pED_Hm = fixed_params['pED_Hm']
    pED_ICU = fixed_params['pED_ICU']

    xi_I = fixed_params['xi_I']
    xi_Hs = fixed_params['xi_Hs']
    xi_Hm = fixed_params['xi_Hm']

    varphi_I = fixed_params['varphi_I']
    varphi_D = fixed_params['varphi_D'] #0.25
    varphi_Hm = fixed_params['varphi_Hm']
    eps_Hs = fixed_params['eps_Hs']

    gamma = fixed_params['gamma']
    eps_Hm = fixed_params['eps_Hm']
    psi_D = fixed_params['psi_D']
    psi_I = fixed_params['psi_I']
    eps_D = fixed_params['eps_D']

    # Compute the analytical equilibirum for W and S, (W*, S*)
    W_star = arrivals_mean / (sigma + omega)
    S_star = sigma * W_star / gamma

    B_Hs_star = pED_Hs * gamma * S_star / xi_Hs
    B_Hm_star = pED_Hm * gamma * S_star / xi_Hm
    B_I_star = pED_ICU * gamma * S_star / xi_I

    # Compute total admissions including those from ED: xi_var * B_var_star external and directs (At_Hs_mean, Ad_Hs_mean  )
    A_Hs = xi_Hs * B_Hs_star + Ad_Hs_mean + At_Hs_mean
    A_Hm = xi_Hm * B_Hm_star + Ad_Hm_mean + At_Hm_mean
    A_I = xi_I * B_I_star + Ad_ICU_mean + At_ICU_mean

    # Reduced system to estimate Hs*, Hm*, I*
    A_mat = np.array([[varphi_I + varphi_D + varphi_Hm, 0, -eps_Hs],
        [-varphi_Hm, psi_I + psi_D, -eps_Hm],
        [-varphi_I, -psi_I, eps_Hs + eps_Hm + eps_D]])
    b_vec = np.array([A_Hs, A_Hm, A_I])
    Hs_star, Hm_star, I_star = np.linalg.solve(A_mat, b_vec)
    D_star = varphi_D * Hs_star + psi_D * Hm_star + eps_D * I_star

    return { "W": W_star, "S": S_star, "B_Hs": B_Hs_star, "B_Hm": B_Hm_star,  "B_I": B_I_star, "Hs": Hs_star,
             "Hm": Hm_star,  "I": I_star, "D": D_star }

def jacobian_at_equilibrium(fixed_params):
    varphi_I = fixed_params['varphi_I']
    varphi_D = fixed_params['varphi_D']
    varphi_Hm = fixed_params['varphi_Hm']
    psi_I = fixed_params['psi_I']
    psi_D = fixed_params['psi_D']
    eps_Hs = fixed_params['eps_Hs']
    eps_Hm = fixed_params['eps_Hm']
    eps_D = fixed_params['eps_D']
    # Jacobian rows correspond to [dHs/dt, dHm/dt, dI/dt, dD/dt] derivatives wrt [Hs,Hm,I,D]
    J = np.array([[-(varphi_I + varphi_D + varphi_Hm), 0, eps_Hs, 0],
        [varphi_Hm, -(psi_I + psi_D), eps_Hm, 0],
        [varphi_I, psi_I, -(eps_Hs + eps_Hm + eps_D), 0],
        [varphi_D, psi_D, eps_D, 0] ])
    # eigenvalues
    eigvals = np.linalg.eigvals(J)
    return J, eigvals


def transient_response_for_multi_surge_ex(surge_specs, times, fixed_params, arrivals_mean, Ad_Hs_mean, Ad_Hm_mean, Ad_ICU_mean, At_Hs_mean, At_Hm_mean, At_ICU_mean ):

    # Baseline equilibrium
    eq = compute_equilibrium_data(fixed_params, arrivals_mean,
        Ad_Hs_mean, Ad_Hm_mean, Ad_ICU_mean, At_Hs_mean, At_Hm_mean, At_ICU_mean )


    x0 = np.array([eq['Hs'], eq['Hm'], eq['I']])
    J_full, eigvals = jacobian_at_equilibrium(fixed_params)
    J = J_full[:3, :3]

    x_ts = np.zeros((len(times), 3))
    x_ts[0] = x0.copy()

    # Precompute equilibrium shifts per surge event
    surge_deltas = []
    for comp, windows in surge_specs.items():
        for (t_on, t_off, amp) in windows:
            xs = compute_equilibrium_data(fixed_params, arrivals_mean,
                amp + Ad_Hs_mean if comp == 'Hs' else Ad_Hs_mean,
                amp + Ad_Hm_mean  if comp == 'Hm' else Ad_Hm_mean,
                amp + Ad_ICU_mean if comp == 'I'  else Ad_ICU_mean,
                At_Hs_mean, At_Hm_mean, At_ICU_mean )
            x_step = np.array([xs['Hs'], xs['Hm'], xs['I']])
            surge_deltas.append((t_on, t_off, x_step - x0))

    # Superposition of linear responses
    for k, t in enumerate(times):
        z = np.zeros(3)
        for (t_on, t_off, delta_eq) in surge_deltas:
            if t < t_on:
                continue
            elif t_on <= t <= t_off:
                tau = t - t_on
                z += (np.eye(3) - expm(J * tau)).dot(delta_eq)
            else:
                tau_s = t_off - t_on
                z_T = (np.eye(3) - expm(J * tau_s)).dot(delta_eq)
                z += expm(J * (t - t_off)).dot(z_T)

        x_ts[k] = x0 + z

    extra_beddays = np.trapz(np.sum(x_ts - x0, axis=1), times)  # total extra bed-days across all 3 comps
    extra_beddays_per_comp = {'Hs': np.trapz(x_ts[:, 0] - x0[0], times),
                              'Hm': np.trapz(x_ts[:, 1] - x0[1], times),
                              'I': np.trapz(x_ts[:, 2] - x0[2], times)}

    # Pack results
    ts_results = {'times': times, 'x_ts': x_ts, 'x0': x0, 'x_step': x_step,
                  'extra_beddays_total': extra_beddays,
                  'extra_beddays_per_comp': extra_beddays_per_comp,
                  'eigvals': eigvals}
    ########
    return ts_results
