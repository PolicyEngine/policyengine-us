from policyengine_us.model_api import *


class pr_exemptions_is_eligible_nonstudent(Variable):
    value_type = bool
    entity = Person
    label = "Puerto Rico dependent exemption eligible nonstudent"
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=28"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(person, period, parameters):
        # if dependent is a student, can earn gross income up to 7500 to be eligible for exemption
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.exemptions.dependent.income_limit
        is_dependent = person("pr_is_tax_unit_dependent", period)
        gross_income = person("pr_gross_income_person", period)
        income_eligibility = gross_income < p.nonstudent
        return is_dependent & income_eligibility
