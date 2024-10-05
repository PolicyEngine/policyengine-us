from policyengine_us.model_api import *


class ia_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "Iowa pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=26"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=26"
    )
    defined_for = "ia_pension_exclusion_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.pension_exclusion
        # determine pension exclusion amount
        pension = person("taxable_pension_income", period)
        filing_status = person.tax_unit("filing_status", period)
        exclusion_cap = p.maximum_amount[filing_status]
        return min_(pension, exclusion_cap)
