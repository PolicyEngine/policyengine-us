from policyengine_us.model_api import *


class spm_unit_allocated_tenant_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tenant payment allocated to the SPM unit for its housing resource cap"
    definition_period = YEAR
    unit = USD
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=14"

    def formula(spm_unit, period, parameters):
        awarded = spm_unit("housing_assistance", period) > 0
        if not awarded.any():
            return np.zeros(spm_unit.count)
        # A4: allocate the contribution of actually awarded program families
        # alongside their subsidy. Census describes a household contribution
        # but does not specify its multi-SPM-unit allocation. This assumption
        # conserves that contribution; a nonrecipient's hypothetical HUD TTP
        # must not reduce another family's allocated housing resource.
        payments = where(awarded, spm_unit("hud_ttp", period), 0).astype("float64")
        simulation = spm_unit.simulation
        household_payments = simulation.map_result(payments, "spm_unit", "household")
        return simulation.map_result(household_payments, "household", "spm_unit")
