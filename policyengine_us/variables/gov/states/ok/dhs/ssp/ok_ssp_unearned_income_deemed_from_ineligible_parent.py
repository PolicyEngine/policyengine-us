from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deemed_income import (
    ssi_parental_deemed_income,
)


class ok_ssp_unearned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma SSP income deemed from ineligible parents"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-6",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-2",
    )
    documentation = (
        "SSI's monthly parental deeming, with the ineligible-child "
        "allocation limited to children younger than 18 (OAC 340:15-1-2)."
    )

    def formula(person, period, parameters):
        supplied = annual_input(
            person, period, "ssi_unearned_income_deemed_from_ineligible_parent"
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR
        # OAC 340:15-1-6(b)(1) imports the state parental-deeming procedure.
        # Keep SSI's allocation amount and its reduction by the child's
        # income; only the children who receive one follow Oklahoma.
        allocations = person(
            "ssi_ineligible_child_allocation_monthly", period
        ) * person("ok_ssp_ineligible_child", period)
        return ssi_parental_deemed_income(person, period, parameters, allocations)
