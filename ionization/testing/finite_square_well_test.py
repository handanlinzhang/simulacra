import logging
import os

import numpy as np

import compy as cp
import ionization as ion
from compy.units import *

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
OUT_DIR = os.path.join(os.getcwd(), 'out', FILE_NAME)

if __name__ == '__main__':
    with cp.utils.Logger('compy', 'ionization', stdout_level = logging.DEBUG) as logger:
        mass = electron_mass
        pw = 200

        bound = 200

        depth = 21.02 * eV
        width = 1.2632 * 2 * bohr_radius

        z_0 = width * np.sqrt(2 * mass * depth) / hbar / 2
        print('z_0 = {},   floor(z_0 / pi / 2) = {},   pi / 2 = {}'.format(z_0, np.ceil(z_0 / (pi / 2)), pi / 2))

        pot = ion.FiniteSquareWell(potential_depth = depth, width = width)
        init = ion.FiniteSquareWellState(well_depth = depth, well_width = width, mass = mass, n = 1)

        print('energy', init.energy / eV)

        states = list(ion.FiniteSquareWellState.all_states_of_well_from_well(pot, mass))
        for state in states:
            print(state, 'with energy', uround(state.energy, eV), 'eV')

        wavenumbers = (twopi / nm) * np.linspace(-10, 10, 1000)
        plane_waves = [ion.OneDFreeParticle(k, mass = mass) for k in wavenumbers]
        dk = np.abs(plane_waves[1].wavenumber - plane_waves[0].wavenumber)

        # electric = ion.SineWave.from_photon_energy(1 * eV, amplitude = .01 * atomic_electric_field,
        #                                            window = ion.SymmetricExponentialTimeWindow(window_time = 10 * fsec, window_width = 1 * fsec, window_center = 5 * fsec))
        # electric = ion.SincPulse(pulse_width = pw * asec, fluence = 1 * Jcm2, phase = 'cos', dc_correction_time = 30 * pw * asec,
        #                          window = ion.SymmetricExponentialTimeWindow(window_time = 29 * pw * asec, window_width = pw * asec / 2))
        electric = ion.NoElectricField()

        ani = [
            ion.animators.LineAnimator(postfix = '_full', target_dir = OUT_DIR, length = 60, distance_unit = 'bohr_radius'),
            ion.animators.LineAnimator(postfix = '_50', target_dir = OUT_DIR, length = 60, plot_limit = 50 * bohr_radius, distance_unit = 'bohr_radius')
        ]

        # test_states = ion.FiniteSquareWellState.all_states_of_well_from_parameters(depth, width, mass) + plane_waves
        test_states = ion.FiniteSquareWellState.all_states_of_well_from_parameters(depth, width, mass)

        sim = ion.LineSpecification('fsw',
                                    x_bound = bound * bohr_radius, x_points = 2 ** 19,
                                    internal_potential = pot,
                                    electric_potential = electric,
                                    test_mass = mass,
                                    test_states = test_states,
                                    dipole_gauges = (),
                                    initial_state = init,
                                    time_initial = -pw * 30 * asec, time_final = pw * 30 * asec, time_step = 1 * asec,
                                    mask = ion.RadialCosineMask(inner_radius = (bound - 50) * bohr_radius, outer_radius = bound * bohr_radius),
                                    animators = ani
                                    ).to_simulation()

        print(sim.info())

        cp.utils.xy_plot('fsw_potential', sim.mesh.x_mesh, pot(distance = sim.mesh.x_mesh),
                         x_scale = 'nm', y_scale = 'eV',
                         target_dir = OUT_DIR)

        print('init norm', sim.mesh.norm)

        sim.mesh.plot_g(name_postfix = '_init', target_dir = OUT_DIR)

        sim.run_simulation()

        print(sim.info())
        print('norm', sim.mesh.norm)
        print('energy EV', sim.energy_expectation_value_vs_time_internal / eV)

        sim.mesh.plot_g(name_postfix = '_post', target_dir = OUT_DIR)
        sim.plot_wavefunction_vs_time(target_dir = OUT_DIR, x_scale = 'asec')
        sim.plot_energy_expectation_value_vs_time(target_dir = OUT_DIR, x_scale = 'asec')

        # overlap_vs_k = np.zeros(len(plane_waves)) * np.NaN
        #
        # for ii, k in enumerate(sorted(s for s in sim.spec.test_states if s in plane_waves)):
        #     overlap = sim.state_overlaps_vs_time[k][-1] * dk
        #     # print('{}: {}'.format(k, overlap))
        #
        #     overlap_vs_k[ii] = overlap
        #
        # print(wavenumbers)
        # print(overlap_vs_k)
        #
        # print(np.sum(overlap_vs_k))
        #
        # cp.utils.xy_plot('overlap_vs_k',
        #                  wavenumbers, overlap_vs_k,
        #                  x_scale = twopi / nm, x_label = r'Wavenumber $k$ ($2\pi/\mathrm{nm}$)',
        #                  y_lower_limit = 0, y_upper_limit = 1,
        #                  target_dir = OUT_DIR)
