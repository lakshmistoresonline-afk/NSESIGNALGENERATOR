"""Model acceptance gate: predictive, economic, stability and drift evidence."""
from __future__ import annotations
import numpy as np


def model_acceptance_gate(metrics: dict, *, min_auc=.52, min_improvement=0.0,
                          max_brier=.25, min_coverage=.05,
                          min_feature_stability=.60, max_psi=.25,
                          max_adversarial_auc=.65, min_profit_factor=1.0,
                          max_drawdown=-.50, require_economic_metrics=True, require_validation_controls=True, require_adversarial_validation=False, require_block_bootstrap_ci=False, require_calibration_ece=False, max_ece=.08, max_cost_stress_sharpe_loss=1.0) -> dict:
    """Strict model-publication gate. Missing required evidence is a failure.

    A model is publishable only when predictive, economic, stability and drift
    evidence are all present and within the configured limits.
    """
    reasons=[]
    required=['auc','brier','log_loss','baseline_logloss','baseline_brier',
              'coverage','feature_stability','max_psi','profit_factor','max_drawdown']
    if require_adversarial_validation or 'adversarial_auc' in metrics:
        required.append('adversarial_auc')
    if require_block_bootstrap_ci:
        required += ['block_bootstrap_ci_lower','block_bootstrap_ci_upper']
    if require_calibration_ece:
        required.append('ece')
    if 'cost_stress_sharpe_loss' in metrics:
        required.append('cost_stress_sharpe_loss')
    if require_validation_controls:
        required += ['cpcv_paths','pbo','dsr_stat','multiple_testing_trials','validation_method','dsr_method']
    for key in required:
        if key in ('validation_method','dsr_method'):
            if not metrics.get(key): reasons.append(f'missing_or_invalid_{key}')
        elif not np.isfinite(metrics.get(key, np.nan)):
            reasons.append(f'missing_or_invalid_{key}')
    auc=metrics.get('auc', np.nan)
    brier=metrics.get('brier', np.nan)
    improvement=metrics.get('baseline_logloss', np.nan)-metrics.get('log_loss', np.nan)
    coverage=metrics.get('coverage', np.nan)
    stability=metrics.get('feature_stability', np.nan)
    psi=metrics.get('max_psi', np.nan)
    adv=metrics.get('adversarial_auc', np.nan)
    ece=metrics.get('ece', np.nan)
    stress_loss=metrics.get('cost_stress_sharpe_loss', np.nan)
    pf=metrics.get('profit_factor', np.nan)
    dd=metrics.get('max_drawdown', np.nan)
    pbo=metrics.get('pbo', np.nan)
    dsr=metrics.get('dsr_stat', np.nan)
    trials=metrics.get('multiple_testing_trials', np.nan)
    if np.isfinite(auc) and auc < min_auc: reasons.append('auc_below_gate')
    if np.isfinite(improvement) and improvement <= min_improvement: reasons.append('no_logloss_improvement')
    if np.isfinite(metrics.get('brier',np.nan)) and brier > max_brier: reasons.append('brier_above_gate')
    if np.isfinite(coverage) and coverage < min_coverage: reasons.append('coverage_too_low')
    if np.isfinite(stability) and stability < min_feature_stability: reasons.append('feature_stability_too_low')
    if np.isfinite(psi) and psi > max_psi: reasons.append('feature_drift_too_high')
    if np.isfinite(adv) and adv > max_adversarial_auc: reasons.append('adversarial_drift_too_high')
    if require_block_bootstrap_ci and np.isfinite(metrics.get('block_bootstrap_ci_lower',np.nan)) and np.isfinite(metrics.get('block_bootstrap_ci_upper',np.nan)) and metrics['block_bootstrap_ci_lower'] <= 0 <= metrics['block_bootstrap_ci_upper']:
        reasons.append('block_bootstrap_return_ci_crosses_zero')
    if require_calibration_ece and np.isfinite(ece) and ece > max_ece: reasons.append('calibration_ece_too_high')
    if np.isfinite(stress_loss) and stress_loss > max_cost_stress_sharpe_loss: reasons.append('cost_stress_degradation_too_high')
    if require_economic_metrics and np.isfinite(pf) and pf < min_profit_factor: reasons.append('profit_factor_below_gate')
    if require_economic_metrics and np.isfinite(dd) and dd < max_drawdown: reasons.append('drawdown_below_gate')
    if require_validation_controls and np.isfinite(pbo) and pbo > .50: reasons.append('pbo_above_gate')
    if require_validation_controls and np.isfinite(dsr) and dsr <= 0: reasons.append('dsr_not_positive')
    if require_validation_controls and np.isfinite(trials) and trials < 1: reasons.append('multiple_testing_registry_empty')
    if require_validation_controls and metrics.get('validation_method') != 'CPCV_CSCV_PBO': reasons.append('unsupported_validation_method')
    if require_validation_controls and metrics.get('dsr_method') != 'finite_trial_expected_max_normal_numerical': reasons.append('unsupported_dsr_method')
    return {'pass': not reasons, 'reasons': sorted(set(reasons))}
