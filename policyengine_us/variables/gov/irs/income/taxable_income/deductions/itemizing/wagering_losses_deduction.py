from policyengine_us.model_api import *


class wagering_losses_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wagering losses deduction"
    unit = USD
    documentation = (
        "Itemized deduction for gambling losses (Schedule A line 16): the "
        "allowed share of losses, up to gambling winnings."
    )
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section165&num=0&edition=prelim",
        # P.L. 119-21 sec. 70114: 90% of losses from 2026
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=96",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.wagering_losses
        # Losses are deductible only against gambling winnings reported on
        # the return. A dependent's gambling is on the dependent's own
        # return, as irs_gross_income leaves their winnings off this one.
        losses = tax_unit_non_dep_add(tax_unit, period, ["gambling_losses"])
        winnings = tax_unit_non_dep_add(tax_unit, period, ["gambling_winnings"])
        return min_(p.rate * losses, winnings)
