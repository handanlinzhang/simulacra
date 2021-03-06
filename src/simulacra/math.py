import logging

import numpy as np
import numpy.random as rand
import scipy.special as special
import scipy.integrate as integ
from typing import Callable, Generator, Iterable

from . import exceptions
from .units import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def rand_phase(shape_tuple):
    """Return random phases (0 to 2pi) in the specified shape."""
    return rand.random_sample(shape_tuple) * twopi


class SphericalHarmonic:
    """A class that represents a spherical harmonic."""

    __slots__ = ('_l', '_m')

    def __init__(self, l: int = 0, m: int = 0):
        """
        Initialize a SphericalHarmonic from its angular momentum numbers.

        Parameters
        ----------
        l
            Orbital angular momentum "quantum number". Must be >= 0.
        m
            Azimuthal angular momentum "quantum number". Must have ``abs(m) <= l``.
        """
        self._l = l
        if not abs(m) <= l:
            raise exceptions.IllegalSphericalHarmonic(f'invalid spherical harmonic: |m| = {abs(m)} must be less than l = {l}')
        self._m = m

    @property
    def l(self) -> int:
        return self._l

    @property
    def m(self) -> int:
        return self._m

    def __str__(self):
        return f'Y_({self.l},{self.m})'

    def __repr__(self):
        return f'{self.__class__.__name__}(l={self.l}, m={self.m})'

    @property
    def latex(self) -> str:
        """Returns a LaTeX-formatted string for the SphericalHarmonic."""
        return fr'Y_{{{self.m}}}^{{{self.l}}}'

    @property
    def _lm(self):
        return self.l, self.m

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._lm == other._lm

    def __hash__(self):
        return hash(self._lm)

    def __le__(self, other):
        return self._lm <= other._lm

    def __ge__(self, other):
        return self._lm >= other._lm

    def __lt__(self, other):
        return self._lm < other._lm

    def __gt__(self, other):
        return self._lm > other._lm

    def __call__(self, theta, phi = 0):
        """
        Evaluate the spherical harmonic at a point, or vectorized over an array of points.

        Parameters
        ----------
        theta : :class:`float`
            The polar coordinate.
        phi : :class:`float`
            The azimuthal coordinate.

        Returns
        -------
        :class:`float`
            The value of the spherical harmonic evaluated at (`theta`, `phi`).
        """
        return special.sph_harm(self.m, self.l, phi, theta)


def complex_quad(integrand: Callable, a: float, b: float, **kwargs) -> (complex, float, float):
    def real_func(*args, **kwargs):
        return np.real(integrand(*args, **kwargs))

    def imag_func(*args, **kwargs):
        return np.imag(integrand(*args, **kwargs))

    real_integral = integ.quad(real_func, a, b, **kwargs)
    imag_integral = integ.quad(imag_func, a, b, **kwargs)

    return real_integral[0] + (1j * imag_integral[0]), real_integral[1:], imag_integral[1:]


def complex_quadrature(integrand: Callable, a: float, b: float, **kwargs) -> (complex, float, float):
    def real_func(*args, **kwargs):
        return np.real(integrand(*args, **kwargs))

    def imag_func(*args, **kwargs):
        return np.imag(integrand(*args, **kwargs))

    real_integral = integ.quadrature(real_func, a, b, **kwargs)
    imag_integral = integ.quadrature(imag_func, a, b, **kwargs)

    return real_integral[0] + (1j * imag_integral[0]), real_integral[1:], imag_integral[1:]


def complex_dblquad(integrand: Callable, a: float, b: float, gfun: Callable, hfun: Callable, **kwargs) -> (complex, float, float):
    def real_func(y, x):
        return np.real(integrand(y, x))

    def imag_func(y, x):
        return np.imag(integrand(y, x))

    real_integral = integ.dblquad(real_func, a, b, gfun, hfun, **kwargs)
    imag_integral = integ.dblquad(imag_func, a, b, gfun, hfun, **kwargs)

    return real_integral[0] + (1j * imag_integral[0]), real_integral[1:], imag_integral[1:]


def complex_nquad(integrand, ranges, **kwargs) -> (complex, float, float):
    def real_func(y, x):
        return np.real(integrand(y, x))

    def imag_func(y, x):
        return np.imag(integrand(y, x))

    real_integral = integ.nquad(real_func, ranges, **kwargs)
    imag_integral = integ.nquad(imag_func, ranges, **kwargs)

    return real_integral[0] + (1j * imag_integral[0]), real_integral[1:], imag_integral[1:]
