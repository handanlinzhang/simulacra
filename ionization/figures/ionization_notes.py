import os
import sys
import logging
import functools as ft

from tqdm import tqdm
import numpy as np
import scipy.optimize as optimize

import matplotlib

matplotlib.use('pgf')

import compy as cp
import ionization as ion
from compy.units import *

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
OUT_DIR = os.path.join(os.getcwd(), 'out', FILE_NAME)

log = cp.utils.Logger('compy', 'ionization', stdout_level = logging.INFO)


pgf_with_latex = {  # setup matplotlib to use latex for output
    "pgf.texsystem": "pdflatex",  # change this if using xetex or lautex
    "text.usetex": True,  # use LaTeX to write all text
    "font.family": "serif",
    "font.serif": [],  # blank entries should cause plots to inherit fonts from the document
    "font.sans-serif": [],
    "font.monospace": [],
    "axes.labelsize": 11,  # LaTeX default is 10pt font.
    "font.size": 11,
    "legend.fontsize": 10,  # Make the legend/label fonts a little smaller
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.figsize": cp.utils.figsize(0.95),  # default fig size of 0.95 \textwidth
    "pgf.preamble": [
        r"\usepackage[utf8x]{inputenc}",  # use utf8 fonts because your computer can handle it :)
        r"\usepackage[T1]{fontenc}",  # plots will be generated using this preamble
    ]
}
matplotlib.rcParams.update(pgf_with_latex)

import matplotlib.pyplot as plt


def save_figure(filename):
    cp.utils.save_current_figure(filename, target_dir = OUT_DIR, img_format = 'pdf')
    cp.utils.save_current_figure(filename, target_dir = OUT_DIR, img_format = 'pgf')


def get_func_name():
    return sys._getframe(1).f_code.co_name


grid_kwargs = {
    # 'dashes': [.5, .5],
    'linestyle': '-',
    'color': 'black',
    'linewidth': .25,
    'alpha': 0.4
}


def sinc_pulse_power_spectrum_full():
    fig = cp.utils.get_figure('full')
    ax = fig.add_subplot(111)

    lower = .15
    upper = .85
    c = (lower + upper) / 2

    omega = np.linspace(-1, 1, 1000)
    power = np.where(np.abs(omega) < upper, 1, 0) * np.where(np.abs(omega) > lower, 1, 0)

    ax.fill_between(omega, 0, power, alpha = 1, edgecolor = 'black', facecolor = 'darkgray')

    delta_line_y_coord = .75
    plt.annotate(s = '', xy = (lower, delta_line_y_coord), xytext = (upper, delta_line_y_coord), textcoords = 'data', arrowprops = dict(arrowstyle = '<->'))
    plt.text(c + .1 * (upper - c), delta_line_y_coord + .025, r'$\Delta_{\omega}$')

    plt.annotate(s = '', xy = (-lower, delta_line_y_coord), xytext = (-upper, delta_line_y_coord), textcoords = 'data', arrowprops = dict(arrowstyle = '<->'))
    plt.text(-c - .1 * (lower - c), delta_line_y_coord + .025, r'$\Delta_{\omega}$')

    ax.set_xlim(-1, 1)
    ax.set_ylim(0, 1.2)

    ax.set_xlabel(r'$   \omega  $')
    ax.set_ylabel(r'$   \left|   \widehat{   \mathcal{E}    }(\omega)  \right|^2   $')
    ax.yaxis.set_label_coords(-.1, .2)

    ax.set_xticks([-upper, -c, -lower, 0, lower, c, upper])
    ax.set_xticklabels([r'$-\omega_{\mathrm{max}}$',
                        r'$-\omega_{\mathrm{c}}$',
                        r'$-\omega_{\mathrm{min}}$',
                        r'$0$',
                        r'$\omega_{\mathrm{min}}$',
                        r'$\omega_{\mathrm{c}}$',
                        r'$\omega_{\mathrm{max}}$'
                        ])
    ax.set_yticks([0, 1])
    ax.set_yticklabels([
        r'$0$',
        r'$\left|   \mathcal{E}_{\omega}      \right|^2$',
    ])

    ax.grid(True, **grid_kwargs)

    save_figure(get_func_name())


def sinc_pulse_power_spectrum_half():
    fig = cp.utils.get_figure('full')
    ax = fig.add_subplot(111)

    lower = .15
    upper = .85
    carrier = (lower + upper) / 2

    omega = np.linspace(0, 1, 1000)
    power = np.where(np.abs(omega) < upper, 1, 0) * np.where(np.abs(omega) > lower, 1, 0)

    ax.fill_between(omega, 0, power, alpha = 1, edgecolor = 'black', facecolor = 'darkgray')

    delta_line_y_coord = .75
    plt.annotate(s = '', xy = (lower, delta_line_y_coord), xytext = (upper, delta_line_y_coord), textcoords = 'data', arrowprops = dict(arrowstyle = '<->'))
    plt.text(carrier + .1 * (upper - carrier), delta_line_y_coord + 0.025, r'$\Delta_{\omega}$')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.2)

    ax.set_xlabel(r'$   \omega  $')
    ax.set_ylabel(r'$   \left|   \widehat{   \mathcal{E}    }(\omega)  \right|^2   $')
    ax.yaxis.set_label_coords(-.1, .2)

    ax.set_xticks([0, lower, carrier, upper])
    ax.set_xticklabels([r'$0$',
                        r'$\omega_{\mathrm{min}}$',
                        r'$\omega_{\mathrm{c}}$',
                        r'$\omega_{\mathrm{max}}$'])
    ax.set_yticks([0, 1])
    ax.set_yticklabels([r'$0$', r'$\left|   \mathcal{E}_{\omega}      \right|^2$'])

    ax.grid(True, **grid_kwargs)

    save_figure(get_func_name())


def sinc_pulse_electric_field(phase = 0):
    fig = cp.utils.get_figure('half')
    ax = fig.add_subplot(111)

    omega_min = twopi
    omega_max = 20 * twopi

    omega_c = (omega_min + omega_max) / 2
    delta = omega_max - omega_min

    time = np.linspace(-1, 1, 1000)
    field = cp.math.sinc(delta * time / 2) * np.cos(omega_c * time + phase * pi)

    ax.plot(time, field, color = 'black', linewidth = 1.5)

    ax.set_xlim(-.18, .18)
    ax.set_ylim(-1.2, 1.2)

    ax.set_xlabel(r'$   t  $')
    ax.set_ylabel(r'$   \mathcal{E}(t)   $')
    ax.yaxis.set_label_coords(-.125, .5)

    d = twopi / delta
    ax.set_xticks([0, -3 * d, -2 * d, -d, d, 2 * d, 3 * d])
    ax.set_xticklabels([r'$0$',
                        r'$ -3 \frac{2\pi}{\Delta_{\omega}}  $',
                        # r'$ -2 \frac{2\pi}{\Delta_{\omega}}   $',
                        r'',
                        r'$ - \frac{2\pi}{\Delta_{\omega}}   $',
                        r'$  \frac{2\pi}{\Delta_{\omega}}   $',
                        # r'$  2 \frac{2\pi}{\Delta_{\omega}}   $',
                        r'',
                        r'$  3 \frac{2\pi}{\Delta_{\omega}}   $',
                        ])

    ax.set_yticks([0, 1, 1 / np.sqrt(2), -1, -1 / np.sqrt(2)])
    ax.set_yticklabels([
        r'$0$',
        r'$\mathcal{E}_{t} $',
        r'$\mathcal{E}_{t} / \sqrt{2} $',
        # r'$ \frac{ \mathcal{E}_{t} }{ \sqrt{2} } $',
        r'$-\mathcal{E}_{t} $',
        r'$-\mathcal{E}_{t} / \sqrt{2} $',
        # r'$ -\frac{ \mathcal{E}_{t} }{ \sqrt{2} } $',
    ])

    ax.grid(True, **grid_kwargs)

    save_figure(get_func_name() + '_phase={}'.format(phase))


def gaussian_pulse_power_spectrum_half():
    # TODO: er, be caereful, is delta for the power spectrum or the amplitude spectrum?
    fig = cp.utils.get_figure('full')
    ax = fig.add_subplot(111)

    carrier = .6
    sigma = .1
    delta = 2 * np.sqrt(2 * np.log(2)) * sigma

    omega = np.linspace(0, 1, 1000)
    power = np.exp(-.5 * (((omega - carrier) / sigma) ** 2)) / np.sqrt(twopi) / sigma
    max_power = np.max(power)
    power /= max_power

    ax.fill_between(omega, 0, power, alpha = 1, edgecolor = 'black', facecolor = 'darkgray')

    delta_line_y_coord = .3
    plt.annotate(s = '', xy = (carrier - delta / 2, delta_line_y_coord), xytext = (carrier + delta / 2, delta_line_y_coord), textcoords = 'data', arrowprops = dict(arrowstyle = '<->'))
    plt.text(carrier + sigma / 5, delta_line_y_coord - .1, r'$\Delta_{\omega}$')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.2)

    ax.set_xlabel(r'$   \omega  $')
    ax.set_ylabel(r'$   \left|   \widehat{   \mathcal{E}    }(\omega)  \right|^2   $')
    ax.yaxis.set_label_coords(-.1, .2)

    ax.set_xticks([0, carrier, carrier - delta / 2, carrier + delta / 2])
    ax.set_xticklabels([r'$0$',
                        r'$  \omega_{\mathrm{c}}  $',
                        r'$  \omega_{\mathrm{c}} - \frac{\Delta}{2}   $',
                        r'$  \omega_{\mathrm{c}} + \frac{\Delta}{2}   $',
                        ])
    ax.set_yticks([0, .5, 1])
    ax.set_yticklabels([
        r'$0$',
        r'$\frac{1}{2}   \left|   \mathcal{E}_{\omega}    \right|^2$',
        r'$\left|   \mathcal{E}_{\omega}      \right|^2$',
    ])

    ax.grid(True, **grid_kwargs)

    save_figure(get_func_name())


def finite_square_well():
    fig = cp.utils.get_figure('full')
    ax = fig.add_subplot(111)

    a_over_two = .5
    depth = -.5

    x = np.linspace(-1, 1, 1000)
    well = np.where(np.abs(x) < a_over_two, depth, 0)
    ax.plot(x, well, linewidth = 1.5, color = 'black')

    ax.set_xlim(-1, 1)
    ax.set_ylim(-.75, .25)

    ax.set_xlabel(r'$   x  $')
    ax.set_ylabel(r'$   V(x)   $')
    ax.yaxis.set_label_coords(-.05, .5)

    ax.set_xticks([0, -a_over_two, a_over_two])
    ax.set_xticklabels([r'$0$',
                        r'$  -\frac{a}{2} $',
                        r'$  \frac{a}{2} $',
                        ])
    ax.set_yticks([0, depth])
    ax.set_yticklabels([
        r'$0$',
        r'$-V_0$',
    ])

    ax.grid(True, **grid_kwargs)

    save_figure(get_func_name())


def finite_square_well_energies():
    fig = cp.utils.get_figure('full')
    ax = fig.add_subplot(111)

    z_0 = 6 * pi / 2 + .5 * np.sqrt(1)  # must make it numpy data type so that the optimizer doesn't panic

    z = np.linspace(0, z_0 + 5, 1000)

    tan = np.tan(z)
    cotan = -1 / np.tan(z)
    sqrt = np.sqrt((z_0 / z) ** 2 - 1)
    sqrt[-1] = 0

    tan[tan < 0] = np.NaN
    cotan[cotan < 0] = np.NaN

    ax.plot(z, tan, color = 'C0', label = r'$\tan(z)$')
    ax.plot(z, cotan, color = 'C1', label = r'$-\cot(z)$')
    ax.plot(z, sqrt, color = 'black', label = r'$   \sqrt{  \left( \frac{z_0}{z} \right)^2  -1 }  $')

    ax.set_xlabel(r'$   z  $')
    # ax.set_ylabel(r'$   \sqrt{  \left( \frac{z_0}{z} \right)^2  -1 }  $')
    # ax.yaxis.set_label_coords(-.05, .5)

    ax.set_xticks([z_0] + list(np.arange(0, z_0 + 5, pi / 2)))
    ax.set_xticklabels([r'$z_0$', r'$0$', r'$\frac{\pi}{2}$'] + [r'${} \frac{{\pi}}{{2}}$'.format(n) for n in range(2, int(z_0 + 5))])

    intersections = []

    for n in np.arange(1, z_0 / (pi / 2) + 1.1, 1):
        left_bound = (n - 1) * pi / 2
        right_bound = min(z_0, left_bound + (pi / 2))

        if n % 2 != 0:  # n is odd
            intersection = optimize.brentq(lambda x: np.tan(x) - np.sqrt(((z_0 / x) ** 2) - 1), left_bound, right_bound)
        else:  # n is even
            intersection = optimize.brentq(lambda x: (1 / np.tan(x)) + np.sqrt(((z_0 / x) ** 2) - 1), left_bound, right_bound)

        intersections.append(intersection)

    intersections = sorted(intersections)
    intersections = np.sqrt((z_0 / intersections) ** 2 - 1)
    ax.set_yticks(intersections)
    ax.set_yticklabels([r'$n={}$'.format(n) for n in range(1, len(intersections) + 1)])

    ax.set_xlim(0, round(z_0 + 2))
    ax.set_ylim(0, 8)

    ax.grid(True, **grid_kwargs)

    ax.legend(loc = 'upper right', framealpha = 1)

    save_figure(get_func_name())


def a_alpha_v2_kernel_gaussian_continuum():
    fig = cp.utils.get_figure('full')
    ax = fig.add_subplot(111)

    dt = np.linspace(-10, 10, 1000)
    tau = .5
    y = 1 / (1 + 1j * (dt / tau))

    ax.plot(dt, np.abs(y), color = 'black', label = r"$\left| K(t-t') \right|$")
    ax.plot(dt, np.real(y), color = 'C0', label = r"$  \mathrm{Re} \left\lbrace K(t-t') \right\rbrace  $")
    ax.plot(dt, np.imag(y), color = 'C1', label = r"$  \mathrm{Im} \left\lbrace K(t-t') \right\rbrace   $")

    ax.set_xlabel(r"$   t-t'  $")
    ax.set_ylabel(r"$   K(t-t') = \left(1 + i \frac{t-t'}{\tau_{\alpha}}\right)^{-1}  $")
    # ax.yaxis.set_label_coords(-., .5)

    ax.set_xticks([0, tau, -tau, 2 * tau, -2 * tau])
    ax.set_xticklabels([r'$0$',
                        r'$\tau_{\alpha}$',
                        r'$-\tau_{\alpha}$',
                        r'$2\tau_{\alpha}$',
                        r'$-2\tau_{\alpha}$',
                        ])

    ax.set_yticks([0, 1, -1, .5, -.5, 1 / np.sqrt(2)])
    ax.set_yticklabels([r'$0$',
                        r'$1$',
                        r'$-1$',
                        r'$1/2$',
                        r'$-1/2$',
                        r'$1/\sqrt{2}$',
                        ])

    ax.set_xlim(-3, 3)
    ax.set_ylim(-.75, 1.4)

    ax.grid(True, **grid_kwargs)

    ax.legend(loc = 'upper right', framealpha = 1)

    save_figure(get_func_name())


def a_alpha_v2_kernel_gaussian_continuum_with_sqrt_gamma():
    fig = cp.utils.get_figure('full')
    ax = fig.add_subplot(111)

    dt = np.linspace(-10, 10, 1000)
    tau = .5
    y = (1 + 1j * (dt / tau)) ** (-3 / 2)

    ax.plot(dt, np.abs(y), color = 'black', label = r"$\left| K(t-t') \right|$")
    ax.plot(dt, np.real(y), color = 'C0', label = r"$  \mathrm{Re} \left\lbrace K(t-t') \right\rbrace  $")
    ax.plot(dt, np.imag(y), color = 'C1', label = r"$  \mathrm{Im} \left\lbrace K(t-t') \right\rbrace   $")

    ax.set_xlabel(r"$   t-t'  $")
    ax.set_ylabel(r"$   K(t-t') = \left(1 + i \frac{t-t'}{\tau_{\alpha}}\right)^{-3/2}  $")
    # ax.yaxis.set_label_coords(-., .5)

    ax.set_xticks([0, tau, -tau, 2 * tau, -2 * tau])
    ax.set_xticklabels([r'$0$',
                        r'$\tau_{\alpha}$',
                        r'$-\tau_{\alpha}$',
                        r'$2\tau_{\alpha}$',
                        r'$-2\tau_{\alpha}$',
                        ])

    ax.set_yticks([0, 1, -1, .5, -.5, 1 / np.sqrt(2)])
    ax.set_yticklabels([r'$0$',
                        r'$1$',
                        r'$-1$',
                        r'$1/2$',
                        r'$-1/2$',
                        r'$1/\sqrt{2}$',
                        ])

    ax.set_xlim(-3, 3)
    ax.set_ylim(-.75, 1.4)

    ax.grid(True, **grid_kwargs)

    ax.legend(loc = 'upper right', framealpha = 1)

    save_figure(get_func_name())


if __name__ == '__main__':
    with log as logger:
        figures = [
            a_alpha_v2_kernel_gaussian_continuum,
            a_alpha_v2_kernel_gaussian_continuum_with_sqrt_gamma,
            finite_square_well,
            finite_square_well_energies,
            sinc_pulse_power_spectrum_full,
            sinc_pulse_power_spectrum_half,
            ft.partial(sinc_pulse_electric_field, phase = 0),
            ft.partial(sinc_pulse_electric_field, phase = 1 / 4),
            ft.partial(sinc_pulse_electric_field, phase = 1 / 2),
            ft.partial(sinc_pulse_electric_field, phase = 1),
            gaussian_pulse_power_spectrum_half,
        ]

        for fig in tqdm(figures):
            fig()