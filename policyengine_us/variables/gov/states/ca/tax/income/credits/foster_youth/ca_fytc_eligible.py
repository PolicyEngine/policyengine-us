from policyengine_us.model_api import *


class ca_fytc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "FYTC Eligible"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth

        age = person("age", period)

        meets_age_requirements = tax_unit.any(
            (age >= p.min_age)
            & (age <= p.max_age)
        )

        eitc_eligibility = tax_unit(
            "ca_eitc_eligible", period
        )

        return meets_age_requirements & eitc_eligibility

