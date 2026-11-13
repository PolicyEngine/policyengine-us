from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deemed_income import (
    ssi_parental_deemed_income,
)


class ssi_unearned_income_deemed_from_ineligible_parent_monthly(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible parent)"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1165"

    def formula(person, period, parameters):
        supplied = annual_input(
            person, period, "ssi_unearned_income_deemed_from_ineligible_parent"
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR
        return ssi_parental_deemed_income(person, period, parameters)
