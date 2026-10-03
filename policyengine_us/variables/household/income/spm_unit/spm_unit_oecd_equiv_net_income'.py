from policyengine_us.model_api import *
from policyengine_us.spm import spm_universe_mask
from spm_calculator.errors import SPMInputError


class spm_unit_oecd_equiv_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Equivalised income"
    unit = USD
    documentation = "Equivalised net income for the SPM unit under the OECD method (divided by the sqare root of the number of persons in the household)"
    definition_period = YEAR
    reference = "https://www.oecd.org/economy/growth/OECD-Note-EquivalenceScales.pdf"

    def formula(spm_unit, period, parameters):
        included = spm_universe_mask(spm_unit, period)
        number_of_people = spm_unit.nb_persons()
        net_income = spm_unit("spm_unit_net_income", period)
        if not np.isfinite(net_income[included]).all():
            raise SPMInputError(
                "SPM_MEASUREMENT_INVALID",
                "Included units require finite SPM resources for equivalised income.",
            )
        return where(included, net_income / (number_of_people**0.5), np.nan)
