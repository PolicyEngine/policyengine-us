from policyengine_us.model_api import *


class ct_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/Schedule-CT-EITC_1222.pdf"
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.ct.tax.income.credits.eitc.rate
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        separate_status = filing_status == filing_statuses.SEPARATE
        agi_separate = tax_unit("adjusted_gross_income_person", period)
        agi_joint = tax_unit("adjusted_gross_income", period)
        return where(
            separate_status,
            eitc * rate * (agi_separate / agi_joint),
            eitc * rate,
        )
