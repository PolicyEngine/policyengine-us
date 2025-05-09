from policyengine_us.model_api import *


class mt_federal_income_tax_deduction_unit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Montana federal income tax deduction for the entire tax unit"
    reference = (
        "https://law.justia.com/codes/montana/2021/title-15/chapter-30/part-21/section-15-30-2131/"
        # MT Code § 15-30-2131 (2021) (1)(b)
    )
    unit = USD
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.itemized.federal_income_tax
        federal_income_tax_limit = p.cap[filing_status]

        federal_income_tax = tax_unit(
            "income_tax_before_refundable_credits", period
        )
        # The federal income tax deduction is attributed to the head in any case
        # as we currently do not have a way to determine individual federal income tax before credits.
        return min_(federal_income_tax, federal_income_tax_limit)
