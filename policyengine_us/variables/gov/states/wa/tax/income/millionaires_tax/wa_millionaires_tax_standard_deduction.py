from policyengine_us.model_api import *


class wa_millionaires_tax_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=13"
    defined_for = StateCode.WA
    documentation = """
    ESSB 6346 Sec. 314 provides a $1,000,000 standard deduction per individual.
    For spouses or state registered domestic partners, their combined standard
    deduction is $1,000,000, regardless of whether they file joint or separate
    returns.

    The deduction is indexed to inflation starting October 2029 for tax year 2030,
    using the Seattle-area CPI-U.
    """
    adds = ["gov.states.wa.tax.income.millionaires_tax.deductions.standard"]
