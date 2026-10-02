from policyengine_us.model_api import *


class ms_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Mississippi LIHEAP regular energy assistance eligibility"
    defined_for = StateCode.MS
    reference = (
        # Rule 6.1 A-D (page 22), Rule 6.3 (page 23) and Rule 6.4 (page 24).
        "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=22",
        # Section 2.3, explanations of policies (page 9).
        "https://liheapch.acf.gov/docs/2026/state-plans/MS_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        size = spm_unit("ms_liheap_household_size", period)
        income = spm_unit("ms_liheap_income", period)
        limit = spm_unit("ms_liheap_income_limit", period)
        has_adult = spm_unit.any(spm_unit.members("age", period) >= p.adult_age)
        # Existing inputs do not establish emancipated-minor headship, institutional
        # residence, or utility account ownership. A household adult is the modeled
        # applicant; children can establish immigration eligibility under Rule 6.3.
        # Rule 6.1 A requires an obligation to pay an energy bill: the main heating
        # fuel, electricity, or energy included in the rent.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        responsible = (
            (spm_unit("heating_expense", period) > 0)
            | (spm_unit("pre_subsidy_electricity_expense", period) > 0)
            | heat_in_rent
        )
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # Rule 6.1 A accepts a bill paid directly to a utility, "subsidized
        # housing where the energy cost is billed separate from rent", or
        # landlord evidence that the utility is "an undesignated portion of the
        # rent". The FY2026 plan (page 9) names public or subsidized housing
        # residents whose rent includes utilities and who are not billed
        # separately for energy, in an incomplete sentence. Both are read as:
        # subsidized housing qualifies only with separately billed energy, and
        # the landlord-evidence route is for unsubsidized renters.
        housing_eligible = ~subsidized | ~heat_in_rent
        return (
            (size > 0) & (income <= limit) & has_adult & responsible & housing_eligible
        )
