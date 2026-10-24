from policyengine_us.model_api import *


class income_driven_repayment_poverty_guideline(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income-driven repayment poverty guideline"
    documentation = (
        "HHS poverty guideline for the tax unit's size. Alaska and Hawaii "
        "residents use their own guidelines; everyone else, including "
        "residents of the territories, uses the 48 contiguous states' "
        "guideline. Tax unit size stands in for the regulation's family size."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(9)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(14)",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.hhs.fpg
        size = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group", period)
        groups = state_group.possible_values
        guideline_group = where(
            state_group == groups.AK,
            "AK",
            where(state_group == groups.HI, "HI", "CONTIGUOUS_US"),
        )
        first_person = p.first_person[guideline_group]
        additional_person = p.additional_person[guideline_group]
        return first_person + additional_person * (size - 1)
