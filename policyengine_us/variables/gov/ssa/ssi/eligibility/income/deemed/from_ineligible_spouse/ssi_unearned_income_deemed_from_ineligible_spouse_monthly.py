from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *


class ssi_unearned_income_deemed_from_ineligible_spouse_monthly(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible spouse)"
    documentation = (
        "This is ignored if total income is under the SSI individual allowance."
    )
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        supplied = annual_input(
            person, period, "ssi_unearned_income_deemed_from_ineligible_spouse"
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR

        # First, determine unearned income from the ineligible spouse.
        # This is (a) in the law.
        ineligible_spouse = person("is_ssi_ineligible_spouse", period)
        unearned_income = person("ssi_unearned_income", period)
        ineligible_spousal_unearned_income = (
            person.marital_unit.sum(ineligible_spouse * unearned_income)
            - ineligible_spouse * unearned_income
        )

        # Next, (b) determine and subtract allocations for ineligible children.
        child_allocations = person("ssi_spousal_deeming_child_allocations", period)
        return max_(0, ineligible_spousal_unearned_income - child_allocations)
