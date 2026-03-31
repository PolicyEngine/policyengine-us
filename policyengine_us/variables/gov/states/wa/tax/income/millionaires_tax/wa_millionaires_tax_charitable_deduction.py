from policyengine_us.model_api import *


class wa_millionaires_tax_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax charitable deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=12"
    defined_for = StateCode.WA
    documentation = """
    ESSB 6346 Sec. 309(1) allows a charitable contribution deduction up to
    $100,000 per individual. For spouses or domestic partners, their combined
    charitable deduction is limited to $100,000, regardless of whether they
    file joint or separate returns.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.tax.income.millionaires_tax.deductions.charitable
        charitable = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        # Cap applies per tax unit (combined for spouses)
        return min_(charitable, p.cap)
