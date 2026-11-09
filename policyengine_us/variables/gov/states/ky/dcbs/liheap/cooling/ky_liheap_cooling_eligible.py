from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.dcbs.liheap.ky_liheap_eligible import (
    ky_liheap_members_documented,
)
from policyengine_us.variables.gov.states.ky.dcbs.liheap.ky_liheap_income_eligible import (
    ky_liheap_meets_income_limit,
)


class ky_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kentucky LIHEAP cooling subsidy eligibility"
    defined_for = StateCode.KY
    reference = (
        "https://www.capky.org/wp-content/uploads/2026/07/FY26-LIHEAP-Summer-Cooling-Subsidy-Fact-Sheet.pdf",
        # Sections 3.1 and 3.4.
        "https://liheapch.acf.gov/docs/2026/state-plans/KY_Plan_2026.pdf#page=10",
        # Sections 2(1)(d) and 4(3)(a).
        "https://apps.legislature.ky.gov/law/kar/titles/921/004/116/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.liheap.cooling
        income_eligible = ky_liheap_meets_income_limit(
            spm_unit, period, parameters, p.fpg_year_lag
        )
        # The household must be responsible for its home electric costs; the
        # subsidy is paid to its electric vendor. Electricity included in
        # rent has no input.
        responsible = spm_unit("has_cooling_expense", period) & (
            spm_unit("pre_subsidy_electricity_expense", period) > 0
        )
        # heating_type is a required input; an unspecified fuel pays nothing.
        # Homes without heating (NONE) and every known fuel can qualify.
        fuel = spm_unit("heating_type", period)
        known_fuel = fuel != fuel.possible_values.UNSPECIFIED
        documented = ky_liheap_members_documented(spm_unit, period)
        return income_eligible & responsible & known_fuel & documented
