#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 20:56:52 2025.

@author: vcsil
"""
from dotenv import dotenv_values
from pathlib import Path


def BUILD_ABSPATH(root, *args):
    """Constroi caminhos absolutos da raiz."""
    path = Path(root).parent.joinpath(*args).resolve()
    return path


ENV = dotenv_values(BUILD_ABSPATH(__file__, ".env"))
