"""Research, validation, drift and governance utilities."""
from .adversarial import adversarial_validation
from .dependence import stationary_block_bootstrap, bootstrap_mean_ci
from .regime_controls import conditional_signal_report, regime_stability_penalty
