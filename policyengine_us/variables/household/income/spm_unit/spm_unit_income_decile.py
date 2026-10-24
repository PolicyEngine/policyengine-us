from policyengine_us.model_api import *
from microdf import MicroSeries
from policyengine_us.spm import spm_universe_mask
from spm_calculator.errors import SPMInputError


class spm_unit_income_decile(Variable):
    value_type = float
    quantity_type = STOCK
    entity = SPMUnit
    label = "Income decile"
    documentation = "The income decile of the SPM unit, person-weighted and using OECD-equivalised net income"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        included = spm_universe_mask(spm_unit, period)
        result = np.full(included.shape, np.nan)
        if not included.any():
            return result
        income = spm_unit("spm_unit_oecd_equiv_net_income", period)
        if not np.isfinite(income[included]).all():
            raise SPMInputError(
                "SPM_MEASUREMENT_INVALID",
                "Included units require finite equivalised SPM income for ranking.",
            )
        weights = spm_unit("spm_unit_weight", period) * spm_unit.nb_persons()
        result[included] = MicroSeries(
            income[included], weights=weights[included]
        ).decile_rank()
        return result
