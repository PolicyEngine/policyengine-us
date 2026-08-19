from policyengine_us.model_api import *


class ia_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "Iowa pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=27",
        "https://revenue.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=26",
    )
    defined_for = "ia_pension_exclusion_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.pension_exclusion
        pension = person("taxable_pension_income", period)
        eligible = person("ia_pension_exclusion_eligible", period)
        eligible_pension = pension * eligible
        filing_status = person.tax_unit("filing_status", period)
        exclusion_cap = p.maximum_amount[filing_status]
        # The cap is a combined limit for the tax unit ("a married couple is
        # allowed a combined exclusion of up to $12,000"); allocate it across
        # eligible spouses in proportion to each one's pension income.
        unit_eligible_pension = person.tax_unit.sum(eligible_pension)
        unit_exclusion = min_(unit_eligible_pension, exclusion_cap)
        denominator = where(unit_eligible_pension > 0, unit_eligible_pension, 1)
        return eligible_pension / denominator * unit_exclusion
