from policyengine_us.model_api import *


class ky_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "Kentucky pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://taxsim.nber.org/historical_state_tax_forms/KY/2021/Form%20740%20Packet%20Instructions-2021.pdf#page=28"
        "https://revenue.ky.gov/Forms/Schedule%20P-2021.pdf"
    )
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.exclusions.pension_income
        # determine pension exclusion amount
        pension = person("taxable_pension_income", period)
        filing_status = person.tax_unit("filing_status", period)
        exclusion_cap = p.maximum_amount[filing_status]
        return min_(pension, exclusion_cap)
