from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deemed_income import (
    ssi_parental_deemed_income,
)


class nh_ssp_unearned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire adult assistance income deemed from ineligible parents"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = (
        "SSI's monthly parental deeming, with the ineligible-child "
        "allocation limited to the siblings He-W 652.03(h)(1) allows."
    )

    def formula(person, period, parameters):
        supplied = annual_input(
            person, period, "ssi_unearned_income_deemed_from_ineligible_parent"
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR
        # Keep SSI's allocation amount and its reduction by the child's
        # income; only the children who receive one follow New Hampshire.
        allocations = person(
            "ssi_ineligible_child_allocation_monthly", period
        ) * person("nh_ssp_ineligible_child", period)
        return ssi_parental_deemed_income(person, period, parameters, allocations)
