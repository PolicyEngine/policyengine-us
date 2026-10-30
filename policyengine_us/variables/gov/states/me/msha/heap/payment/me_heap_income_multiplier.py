from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg

# Numerical tolerances, not policy values: results are rounded to this many
# decimals before the rule's rounding so floating-point error (for example
# 25 x 1.1 x 4/5 = 22.000000000000004) cannot cross a rounding or band
# boundary.
FLOAT_GUARD_DECIMALS = 6


class me_heap_income_multiplier(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = "/1"
    label = "Maine HEAP income multiplier"
    defined_for = StateCode.ME
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ME_BenefitMatrix_2026.pdf#page=2",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/346c024.docx",
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=17",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.me.msha.heap
        size = spm_unit("me_heap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        poverty_level = spm_unit("me_heap_income", period) / guideline
        # Round half up to the edition's increment, then look up the band.
        increment = p.points.poverty_level_rounding_increment
        increments = np.round(poverty_level / increment, FLOAT_GUARD_DECIMALS)
        rounded = np.floor(increments + 0.5) * increment
        return p.points.income_multiplier.calc(np.round(rounded, FLOAT_GUARD_DECIMALS))
