"""Single entry point for research/model governance decisions."""
from .model_gate import model_acceptance_gate
from .drift import frame_psi


def evaluate_model_governance(metrics: dict, reference=None, current=None, **kwargs):
    result=dict(metrics)
    if reference is not None and current is not None:
        drift=frame_psi(reference,current)
        result.update({'max_psi':drift['max_psi'],'median_psi':drift['median_psi']})
    result['gate']=model_acceptance_gate(result, **kwargs)
    return result
