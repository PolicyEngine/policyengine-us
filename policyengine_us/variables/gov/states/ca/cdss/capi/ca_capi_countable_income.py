from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._ssi_countable_income import (
    ssi_countable_income,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deemed_income import (
    ssi_parental_deemed_income,
)


class ca_capi_countable_income(Variable):
    value_type = float
    entity = Person
    label = "California CAPI countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    # Counties apply SSI income and deeming steps under MPP 49-035.12,
    # .71 and .722 (PDF pages 25 and 30).
    reference = (
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=30"
    )

    def formula(person, period, parameters):
        supplied = annual_input(person, period, "ssi_countable_income")
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR

        supplied_parent_deemed = annual_input(
            person, period, "ssi_unearned_income_deemed_from_ineligible_parent"
        )
        if supplied_parent_deemed is not None:
            parent_deemed = supplied_parent_deemed / MONTHS_IN_YEAR
        else:
            # Counties divide parental income among SSI and CAPI children.
            immigration_status = person("immigration_status", period)
            is_citizen = (
                immigration_status == immigration_status.possible_values.CITIZEN
            )
            ssi_recipient = person("is_ssi_aged_blind_disabled", period.this_year) & (
                is_citizen | person("is_ssi_qualified_noncitizen", period.this_year)
            )
            recipients = person("is_child", period.this_year) & (
                ssi_recipient | person("ca_capi_eligible_person", period.this_year)
            )
            parent_deemed = ssi_parental_deemed_income(
                person, period, parameters, recipients=recipients
            )

        return ssi_countable_income(
            person, period, parameters, parent_deemed=parent_deemed
        )
