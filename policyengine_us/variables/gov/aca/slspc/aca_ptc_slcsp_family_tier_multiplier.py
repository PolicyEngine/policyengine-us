from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_multiplier import (
    family_tier_multiplier,
)


class aca_ptc_slcsp_family_tier_multiplier(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA family tier multiplier for the premium tax credit coverage family"
    unit = "/1"
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"
    reference = "https://www.law.cornell.edu/cfr/text/26/1.36B-3#f"

    def formula(tax_unit, period, parameters):
        family_category = tax_unit("aca_ptc_slcsp_family_tier_category", period)
        covered = tax_unit.members("is_aca_coverage_family_member", period.this_year)
        return family_tier_multiplier(
            tax_unit, period, parameters, family_category, covered
        )
