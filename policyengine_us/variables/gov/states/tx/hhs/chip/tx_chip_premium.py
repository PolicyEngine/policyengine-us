from policyengine_us.model_api import *


class tx_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Texas CHIP enrollment fee"
    unit = USD
    documentation = (
        "Annual Texas CHIP enrollment fee. One fee per household, tiered by "
        "modified adjusted gross income as a fraction of the federal poverty "
        "line. Families with at least one CHIP-eligible member pay the fee."
    )
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/d-1820-enrollment-fees"

    def formula(tax_unit, period, parameters):
        has_chip_member = add(tax_unit, period, ["is_chip_eligible"]) > 0
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.tx.hhs.chip.enrollment_fee
        return has_chip_member * p.calc(income_level)
