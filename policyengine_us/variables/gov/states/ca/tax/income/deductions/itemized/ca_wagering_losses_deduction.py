from policyengine_us.model_api import *


class ca_wagering_losses_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California wagering losses deduction"
    unit = USD
    documentation = (
        "California itemized deduction for gambling losses, up to gambling "
        "winnings. California does not apply the federal 90% limit that "
        "starts in 2026. California Lottery winnings are exempt and "
        "California Lottery losses are not deductible; the gambling inputs "
        "do not separate them, so they are treated as other gambling."
    )
    definition_period = YEAR
    reference = (
        # 2025 Form 540 booklet: Schedule CA (540) line 8b (California
        # Lottery winnings), Part II line 16 (gambling losses) and the
        # Itemized Deductions Worksheet
        # PDF pages 62, 67-68
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=62",
        # California conforms to the Internal Revenue Code as of January 1,
        # 2025, before P.L. 119-21.
        "https://www.ftb.ca.gov/tax-pros/law/conformity.html",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # 26 U.S.C. 165(d) before P.L. 119-21: all losses, up to the gains.
        # Dependents report their gambling on their own returns.
        losses = tax_unit_non_dep_add(tax_unit, period, ["gambling_losses"])
        winnings = tax_unit_non_dep_add(tax_unit, period, ["gambling_winnings"])
        return min_(losses, winnings)
