from policyengine_us.model_api import *


class ky_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://taxsim.nber.org/historical_state_tax_forms/KY/2021/Form%20740%20Packet%20Instructions-2021.pdf#page=28"
        "https://revenue.ky.gov/Forms/Schedule%20P-2021.pdf"
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=24"
        "https://revenue.ky.gov/Forms/Schedule%20P%202022.pdf"
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ky.tax.income.exclusions.pension_income
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = is_head | is_spouse
        # determine pension exclusion amount
        pension = person("taxable_pension_income", period)
        eligible_pension = pension * head_or_spouse
        total_pension = tax_unit.sum(eligible_pension)
        filing_status = tax_unit("filing_status", period)
        exclusion_cap = p.maximum_amount[filing_status]
        return min_(total_pension, exclusion_cap)
