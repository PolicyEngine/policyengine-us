from policyengine_us.model_api import *


class ny_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/614",
        # Standard deduction table: the dependent amount applies only to
        # filing status 1, "Single and you marked item C Yes".
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=11",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        single = filing_status == filing_status.possible_values.SINGLE
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(
            single & dependent_elsewhere,
            p.dependent_elsewhere,
            p.amount[filing_status],
        )
