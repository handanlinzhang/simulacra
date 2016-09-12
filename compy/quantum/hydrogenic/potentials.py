import logging

import numpy as np

from compy import utils
import compy.units as un

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Potential:
    """
    A class that represents a potential, defined over some kwargs.

    The result of a call to a Potential should be the potential energy / charge (V = J/C for electric interactions, V = J/kg for gravitational interactions, etc.) at the coordinates given by kwargs.
    
    Caution: use numpy meshgrids to vectorize over multiple kwargs.
    """

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{}'.format(self.__class__.__name__)

    def __add__(self, other):
        return PotentialSum(self, other)


class PotentialSum:
    """
    A class that handles a group of potentials that should be evaluated together to produce a total potential.

    Caution: the potentials are summed together with no check as to the structure of the sum. Use numpy meshgrids to vectorize over multiple kwargs.
    """

    def __init__(self, *potentials):
        self.potentials = potentials

    def __str__(self):
        return 'Potentials: {}'.format(', '.join([str(p) for p in self.potentials]))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join([repr(p) for p in self.potentials]))

    def __call__(self, **kwargs):
        return sum(p(**kwargs) for p in self.potentials)

    def __add__(self, other):
        try:
            result = PotentialSum(*self.potentials, other.potentials)
        except AttributeError:
            result = PotentialSum(*self.potentials, other)
        return result


class NuclearPotential(Potential):
    """A Potential representing the electric potential of the nucleus of a hydrogenic atom."""

    def __init__(self, charge = 1 * un.proton_charge):
        super(NuclearPotential, self).__init__()

        self.charge = charge

    def __repr__(self):
        return '{}(charge = {})'.format(self.__class__.__name__, self.charge)

    def __str__(self):
        return '{}(charge = {} e)'.format(self.__class__.__name__, un.round(self.charge, un.proton_charge, 3))

    def __call__(self, r = None, test_charge = None, **kwargs):
        return un.coulomb_force_constant * self.charge * test_charge / r


class RadialImaginaryPotential(Potential):
    def __init__(self, center = 20 * un.bohr_radius, width = 2 * un.bohr_radius, amplitude = 1 * un.atomic_electric_field):
        """
        Construct a RadialImaginaryPotential. The potential is shaped like a Gaussian and has an imaginary amplitude.

        A positive/negative amplitude yields an imaginary potential that causes decay/amplification.

        :param center: the radial coordinate to center the potential on
        :param width: the width (FWHM) of the Gaussian
        :param amplitude: the peak amplitude of the Gaussian
        """
        self.center = center
        self.width = width
        self.amplitude = amplitude

        self.prefactor = -1j * self.amplitude * (un.proton_charge ** 2)

    def __call__(self, r = None, **kwargs):
        return self.prefactor * np.exp(-(((r - self.center) / self.width) ** 2))


class UniformLinearlyPolarizedElectricField(Potential):
    def __init__(self, window_time = None, window_width = None):
        super(UniformLinearlyPolarizedElectricField, self).__init__()

        self.window_time = window_time
        self.window_width = window_width

    def get_window(self, t):
        if self.window_time is not None and self.window_width is not None:
            return 1 / (1 + np.exp(-(t + self.window_time) / self.window_width)) - 1 / (1 + np.exp(-(t - self.window_time) / self.window_width))
        else:
            return 1

    def get_amplitude(self, t):
        raise NotImplementedError

    def __call__(self, t = None, distance_along_polarization = None, test_charge = None, **kwargs):
        return distance_along_polarization * test_charge * self.get_amplitude(t)


class Rectangle(UniformLinearlyPolarizedElectricField):
    def __init__(self, start_time = 0 * un.asec, end_time = 50 * un.asec, amplitude = 1 * un.atomic_electric_field, **kwargs):
        super(Rectangle, self).__init__(**kwargs)

        self.start_time = start_time
        self.end_time = end_time
        self.amplitude = amplitude

    def __str__(self):
        out = '{}(start_time = {} as, end_time = {} as, amplitude = {} AEF'.format(self.__class__.__name__,
                                                                                   un.round(self.start_time, un.asec, 3),
                                                                                   un.round(self.end_time, un.asec, 3),
                                                                                   un.round(self.amplitude, un.twopi, 3))

        if self.window_time is not None and self.window_width is not None:
            out += ', window_time = {} as, window_width = {} as'.format(un.round(self.window_time, un.asec, 3),
                                                                        un.round(self.window_width, un.asec, 3))

        out += ')'

    def __repr__(self):
        out = '{}(start_time = {}, end_time = {}, amplitude = {}'.format(self.__class__.__name__,
                                                                         self.start_time,
                                                                         self.end_time,
                                                                         self.amplitude)

        if self.window_time is not None and self.window_width is not None:
            out += ', window_time = {}, window_width = {}'.format(self.window_time,
                                                                  self.window_width)

        out += ')'

        return out

    def get_amplitude(self, t):
        cond = np.greater_equal(t, self.start_time) * np.less_equal(t, self.end_time)
        on = np.ones(np.shape(t))
        off = np.zeros(np.shape(t))

        out = np.where(cond, on, off) * self.amplitude * self.get_window(t)

        return out


class SineWave(UniformLinearlyPolarizedElectricField):
    def __init__(self, omega, amplitude = 1 * un.atomic_electric_field, phase = 0, **kwargs):
        super(SineWave, self).__init__(**kwargs)

        self.omega = omega
        self.phase = phase % un.twopi
        self.amplitude = amplitude

    def __str__(self):
        out = '{}(omega = 2pi * {} THz, amplitude = {} AEF, phase = 2pi * {}'.format(self.__class__.__name__,
                                                                                     un.round(self.frequency, un.THz, 3),
                                                                                     un.round(self.amplitude, un.atomic_electric_field, 3),
                                                                                     un.round(self.phase, un.twopi, 3))

        if self.window_time is not None and self.window_width is not None:
            out += ', window_time = {} as, window_width = {} as'.format(un.round(self.window_time, un.asec, 3),
                                                                        un.round(self.window_width, un.asec, 3))

        out += ')'

        return out

    def __repr__(self):
        out = '{}(omega = {}, amplitude = {}, phase = {}'.format(self.__class__.__name__,
                                                                 self.omega,
                                                                 self.amplitude,
                                                                 self.phase)

        if self.window_time is not None and self.window_width is not None:
            out += ', window_time = {}, window_width = {}'.format(self.window_time,
                                                                  self.window_width)

        out += ')'

        return out

    @classmethod
    def from_frequency(cls, frequency, amplitude, phase = 0, window_time = None, window_width = None):
        return cls(frequency * un.twopi, amplitude, phase = phase, window_time = window_time, window_width = window_width)

    @property
    def frequency(self):
        return self.omega / un.twopi

    @frequency.setter
    def frequency(self, frequency):
        self.omega = frequency * un.twopi

    @property
    def period(self):
        return 1 / self.frequency

    @period.setter
    def period(self, period):
        self.frequency = 1 / period

    def get_amplitude(self, t):
        return self.amplitude * np.sin((self.omega * t) + self.phase) * self.get_window(t)

    def get_peak_amplitude(self):
        return self.amplitude

    def get_peak_power_density(self):
        return un.c * un.epsilon_0 * (np.abs(self.amplitude) ** 2)
