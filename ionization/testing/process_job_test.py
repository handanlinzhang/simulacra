import os
import logging
from pprint import pprint

import compy as cp
from compy.units import *
import ionization as ion
import ionization.cluster as clu

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
OUT_DIR = os.path.join(os.getcwd(), 'out', FILE_NAME)

if __name__ == '__main__':
    with cp.utils.Logger('compy', 'ionization', stdout_logs = True, stdout_level = logging.CRITICAL):
        # job_name = 'both_phases'
        job_name = 'both_phases__multi_fluence__min_time'
        # job_name = 'both_phases__multi_fluence__min_time__extra_l'
        job_dir = os.path.join(OUT_DIR, job_name)

        try:
            jp = clu.SincPulseJobProcessor.load(os.path.join(job_dir, job_name + '.job'))
        except FileNotFoundError:
            jp = clu.SincPulseJobProcessor(job_name, job_dir)

        jp.process_job(individual_processing = False)

        jp.save(target_dir = job_dir)

        print(jp)
        with open(os.path.join(job_dir, 'data.txt'), mode = 'w') as f:
            pprint(jp.data, stream = f)

        jp.make_plot('diag', 'file_name',
                     clu.KeyFilterLine('run_time', label = 'Run Time'),
                     clu.KeyFilterLine('elapsed_time', label = 'Elapsed Time'),
                     target_dir = job_dir,
                     y_scale = 'hours', y_label = 'Time to Complete',
                     x_scale = 'asec', x_label = 'Simulation Pulse Width')

        phases, fluences = jp.parameter_sets['phase'], jp.parameter_sets['fluence']

        final_initial_state_lines = [clu.KeyFilterLine(key = 'final_initial_state_overlap',
                                                       filters = (clu.check('phase', phase), clu.check('fluence', fluence)),
                                                       label = 'phase = {}, fluence = {} J/cm^2'.format(phase, uround(fluence, J / (cm ** 2), 3)))
                                     for phase in phases for fluence in fluences]
        jp.make_plot('final_initial_state_vs_pulse_width',
                     'pulse_width',
                     *final_initial_state_lines,
                     target_dir = job_dir,
                     y_label = 'Norm',
                     x_scale = 'asec', x_label = 'Pulse Width')
        jp.make_plot('final_initial_state_vs_pulse_width_log',
                     'pulse_width',
                     *final_initial_state_lines,
                     target_dir = job_dir,
                     y_label = 'Norm', y_log_axis = True,
                     x_scale = 'asec', x_label = 'Pulse Width')

        final_norm_lines = [clu.KeyFilterLine(key = 'final_norm',
                                              filters = (clu.check('phase', phase), clu.check('fluence', fluence)),
                                              label = 'phase = {}, fluence = {} J/cm^2'.format(phase, uround(fluence, J / (cm ** 2), 3)))
                            for phase in phases for fluence in fluences]
        jp.make_plot('final_norm_vs_pulse_width',
                     'pulse_width',
                     *final_norm_lines,
                     target_dir = job_dir,
                     y_label = 'Norm',
                     x_scale = 'asec', x_label = 'Pulse Width')
        jp.make_plot('final_norm_vs_pulse_width_log',
                     'pulse_width',
                     *final_norm_lines,
                     target_dir = job_dir,
                     y_label = 'Norm', y_log_axis = True,
                     x_scale = 'asec', x_label = 'Pulse Width')
        # jp.make_plot('pulse_width', 'final_norm', filter = lambda v: v['phase'] == 'sin',
        #              name = 'sin', target_dir = job_dir,
        #              y_label = 'Norm',
        #              x_scale = 'asec', x_label = 'Pulse Width')

        # jp.make_plot('pulse_width', 'final_initial_state_overlap', filter = lambda v: v['phase'] == 'cos',
        #              name = 'cos', target_dir = job_dir,
        #              y_label = 'Final Initial State Overlap',
        #              x_scale = 'asec', x_label = 'Pulse Width')
        # jp.make_plot('pulse_width', 'final_initial_state_overlap', filter = lambda v: v['phase'] == 'sin',
        #              name = 'sin', target_dir = job_dir,
        #              y_label = 'Final Initial State Overlap',
        #              x_scale = 'asec', x_label = 'Pulse Width')
        #
        # jp.make_plot('pulse_width', 'final_initial_state_overlap', filter = lambda v: v['phase'] == 'cos',
        #              name = 'cos_log', target_dir = job_dir,
        #              y_label = 'Final Initial State Overlap', log_y = True,
        #              x_scale = 'asec', x_label = 'Pulse Width')
        # jp.make_plot('pulse_width', 'final_initial_state_overlap', filter = lambda v: v['phase'] == 'sin',
        #              name = 'sin_log', target_dir = job_dir,
        #              y_label = 'Final Initial State Overlap', log_y = True,
        #              x_scale = 'asec', x_label = 'Pulse Width')
        #
        # jp.make_plot('pulse_width', 'final_initial_state_overlap', filter = (lambda v: v['phase'] == 'cos', lambda v: v['phase'] == 'sin'),
        #              legends = ('Cos', 'Sin'),
        #              name = 'both_log', target_dir = job_dir,
        #              y_label = 'Final Initial State Overlap', log_y = True,
        #              x_scale = 'asec', x_label = 'Pulse Width')
