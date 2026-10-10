from policyengine_us.model_api import *


class ny_wagering_losses_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY wagering losses deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        # Form IT-196 instructions, line 29: gambling losses
        "https://www.tax.ny.gov/pdf/2025/inc/it196i_2025.pdf#page=16",
    )
    defined_for = StateCode.NY
    documentation = """
    NY Tax Law § 615 requires itemized deductions to be computed using
    pre-TCJA federal rules. New York allows gambling losses up to gambling
    winnings under the federal rules that applied to tax year 2017, so the
    federal 90% limit that starts in 2026 does not apply.
    """

    def formula(tax_unit, period, parameters):
        # Dependents report their gambling on their own returns.
        losses = tax_unit_non_dep_add(tax_unit, period, ["gambling_losses"])
        winnings = tax_unit_non_dep_add(tax_unit, period, ["gambling_winnings"])
        return min_(losses, winnings)
