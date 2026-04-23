from policyengine_us.model_api import *


class mo_head_of_household_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri head of household additional exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mo.gov/main/OneSection.aspx?section=143.161",
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2024.pdf#page=8",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        eligible = (filing_status == statuses.HEAD_OF_HOUSEHOLD) | (
            filing_status == statuses.SURVIVING_SPOUSE
        )
        p = parameters(period).gov.states.mo.tax.income.exemptions
        return eligible * p.head_of_household
