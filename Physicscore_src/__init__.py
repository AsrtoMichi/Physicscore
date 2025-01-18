"""
# Physicscore
This app is aimed at counting points in physic competitions.
The app consists of two windows: one for viewing the scores,
one for entering answers and jolly (only one for team).
It also saves all answer and jolly in a .json file, to make grafic.
"""

from .ReportGenerator import generate_report
from .Physicscore import Physicscore


__all__ = ["Physicscore, generate_report"]

__author__ = "AsrtoMichi"
__source_code__ = "https://github.com/AsrtoMichi/Physicscore"
__version__ = "v0.1.1.0"
__credits__ = """
Alessandro Chiozza, Federico Micelli, Giorgio Sorgente and Gabriele Trisolino for technical help
"""