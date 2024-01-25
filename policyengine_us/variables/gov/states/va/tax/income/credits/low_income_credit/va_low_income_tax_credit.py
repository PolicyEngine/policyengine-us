from policyengine_us.model_api import *


class va_low_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia low income tax credit"
    unit = USD
    reference = (
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32",
        "https://law.lis.virginia.gov/vacodeupdates/title58.1/section58.1-339.8/",
    )

    definition_period = YEAR
    defined_for = "va_low_income_tax_credit_agi_eligible"

    def formula(tax_unit, period, parameters):
        exemptions = tax_unit("va_personal_exemption", period)
        p = parameters(
            period
        ).gov.states.va.tax.income.credits.eitc.low_income_tax
        return p.base * exemptions
