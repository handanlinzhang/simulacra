import itertools
import logging
import os
import pickle
import sys
from copy import deepcopy
import textwrap
from pathlib import Path
from typing import Any, Iterable, Optional, Callable, Type, Tuple, Union, List, Collection, Dict

from tqdm import tqdm

from .. import sims, utils

# these imports need to be here so that ask_for_eval works
import numpy as np
import scipy as sp
from .. import units as u

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Parameter:
    """A class that represents a parameter of a :class:`Specification`."""

    def __init__(self, name: str, value: Any = None, expandable: bool = False):
        """
        Parameters
        ----------
        name
            The name of the Parameter, which should match a keyword argument of the target :class:`Specification`.
        value
            The value of the Parameter, or an iterable of values.
        expandable
            If True, :func:`expand_parameters` will expand along an iterable `value`.
        """
        self.name = name
        self.value = value
        self.expandable = expandable

    def __repr__(self):
        if not self.expandable:
            return f'{self.__class__.__name__}(name = {self.name}, value = {self.value})'
        else:
            header = f'{self.__class__.__name__}(name = {self.name}, expandable = {self.expandable}, values ='
            val_text = textwrap.wrap(', '.join(repr(v) for v in self.value), width = 60)
            out = '\n    '.join([header] + val_text) + ')'

            return out


def expand_parameters(parameters: Collection[Parameter]) -> List[Dict[str, Any]]:
    """
    Expand an iterable of :class:`Parameter` to a list of dictionaries containing all of the combinations of parameter values.
    Each of these dictionaries can then be unpacked into a :class:`Specification`.

    If a :class:`Parameter` has ``expandable = True``, it will be expanded across the values in the outermost iterable in that :class:`Parameter`'s ``value``.

    Parameters
    ----------
    parameters
        The parameters to expand over.

    Returns
    -------
    parameter_combinations
        An list of dictionaries containing all of the combinations of parameters.
    """
    dicts = [{}]

    for par in parameters:
        # make sure the value is an iterable that isn't a string and has a length
        if par.expandable and hasattr(par.value, '__iter__') and not isinstance(par.value, str) and hasattr(par.value, '__len__'):
            dicts = [deepcopy(d) for d in dicts for _ in range(len(par.value))]
            for d, v in zip(dicts, itertools.cycle(par.value)):
                d[par.name] = v
        else:
            for d in dicts:
                d[par.name] = par.value

    return dicts


def ask_for_input(question: str, default: Any = None, cast_to: Type = str) -> Any:
    """
    Ask for input from the user, with a default value, which will be cast to a specified type.

    Parameters
    ----------
    question
        A string to display on the command prompt for the user.
    default
        The default answer to the question.
    cast_to
        A type to cast the user's input to.

    Returns
    -------

    """
    input_str = input(question + ' [Default: {}] > '.format(default))

    trimmed = input_str.replace(' ', '')
    if trimmed == '':
        return default

    try:
        out = cast_to(trimmed)
    except Exception as e:
        print(e)
        return ask_for_input(question, default = default, cast_to = cast_to)

    logger.debug('Got input from stdin for question "{}": {}'.format(question, out))

    return out


def ask_for_choices(question: str, choices: Dict[str, Any], default: Optional[str] = None):
    if default is None:
        default = list(choices.keys())[0]
    return choices[ask_for_input(question + f' [{" | ".join(choices)}]', default = default)]


def ask_for_bool(question: str, default: Union[str, bool] = False) -> bool:
    """
    Ask for input from the user, with a default value, which will be interpreted as a boolean.

    Synonyms for True: 'true', 't', 'yes', 'y', '1', 'on'
    Synonyms for False: 'false', 'f', 'no', 'n', '0', 'off'

    Parameters
    ----------
    question : :class:`str`
        A string to display on the command prompt for the user.
    default : :class:`str`
        The default answer to the question.

    Returns
    -------
    answer
        The input, interpreted as a boolean.
    """
    try:
        input_str = input(question + ' [Default: {}] > '.format(default))

        trimmed = input_str.replace(' ', '').lower()
        if trimmed == '':
            trimmed = default

        logger.debug('Got input from stdin for question "{}": {}'.format(question, input_str))

        if trimmed in ('true', 't', 'yes', 'y', '1', 'on', True):
            return True
        elif trimmed in ('false', 'f', 'no', 'n', '0', 'off', False):
            return False
        else:
            raise ValueError('Invalid answer to question "{}"'.format(question))
    except Exception as e:
        print(e)
        return ask_for_bool(question, default = default)


def ask_for_eval(question: str, default: str = 'None') -> Any:
    """
    Ask for input from the user, with a default value, which will be evaluated as a Python command.

    Numpy and Scipy's top-level interfaces (imported as ``np`` and ``sp``) and Simulacra's own unit module (imported as ``u``) are both available.
    For example, ``'np.linspace(0, twopi, 100)'`` will produce the expected result of 100 numbers evenly spaced between zero and twopi.

    NB: this function is not safe!
    The user can execute arbitrary Python code!

    Parameters
    ----------
    question
        A string to display on the command prompt for the user.
    default
        The default answer to the question.

    Returns
    -------
    answer

    """
    input_str = input(question + ' [Default: {}] (eval) > '.format(default))

    trimmed = input_str.replace(' ', '')
    if trimmed == '':
        input_str = str(default)

    logger.debug('Got input from stdin for question "{}": {}'.format(question, input_str))

    try:
        return eval(input_str)
    except Exception as e:
        print(e)
        return ask_for_eval(question, default = default)


def abort_job_creation():
    """Abort job creation by exiting the script."""
    print('Aborting job creation...')
    logger.critical('Aborted job creation')
    sys.exit(0)


def create_job_subdirs(job_dir: str, subdirs = ('inputs', 'outputs', 'logs')):
    """Create directories for the inputs, outputs, logs, and movies."""
    print('Creating job directory and subdirectories...')

    job_dir = Path(job_dir)
    job_dir.mkdir(parents = True, exist_ok = True)
    for subdir in subdirs:
        (job_dir / subdir).mkdir(parents = True, exist_ok = True)


def save_specifications(specifications: Iterable[sims.Specification], job_dir: Union[Path, str]):
    """Save a list of Specifications."""
    print('Saving Specifications...')

    for spec in tqdm(specifications, ascii = True):
        spec.save(target_dir = Path(job_dir) / 'inputs')

    logger.debug('Saved Specifications')


def write_specifications_info_to_file(
    specifications: Collection[sims.Specification],
    job_dir: Union[Path, str],
):
    """Write information from the list of the Specifications to a file."""
    print('Writing Specification info to file...')

    path = Path(job_dir) / 'specifications.txt'
    text = '\n'.join(str(spec.info()) for spec in specifications)
    with path.open(mode = 'w', encoding = 'utf-8') as file:
        file.write(text)

    logger.debug('Wrote Specification information to file')

    return path


def write_parameters_info_to_file(parameters: Iterable[Parameter], job_dir: str):
    """Write information from the list of Parameters to a file."""
    print('Writing parameters to file...')

    path = Path(job_dir) / 'parameters.txt'
    text = '\n'.join(repr(param) for param in parameters)
    with path.open(mode = 'w', encoding = 'utf-8') as file:
        file.write(text)

    logger.debug('Wrote parameter information to file')


def specification_check(specifications: Collection[sims.Specification], check: int = 3):
    """Ask the user whether some number of specifications look correct."""
    print('-' * 20)
    for s in specifications[0:check]:
        print(f'\n{s.info()}\n')
        print('-' * 20)

    print(f'Generated {len(specifications)} Specifications')

    check = ask_for_bool(f'Do the first {check} Specifications look correct?', default = 'No')
    if not check:
        abort_job_creation()


def write_job_info_to_file(job_info, job_dir: Union[Path, str]):
    """Write job information to a file."""
    path = Path(job_dir) / 'info.pkl'
    with path.open(mode = 'wb') as file:
        pickle.dump(job_info, file, protocol = -1)


def load_job_info_from_file(job_dir: Union[Path, str]):
    """Load job information from a file."""
    path = Path(job_dir) / 'info.pkl'
    with path.open(mode = 'rb') as file:
        return pickle.load(file)
