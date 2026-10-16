"""Fixtures compartilhadas para a suíte de testes."""

from __future__ import annotations

import pytest

from mlops_registro_drift.registry import FIXED_CLOCK


@pytest.fixture
def fixed_clock():
    """Relógio fixo para tornar determinísticos os testes de registro/pipeline."""
    return lambda: FIXED_CLOCK
