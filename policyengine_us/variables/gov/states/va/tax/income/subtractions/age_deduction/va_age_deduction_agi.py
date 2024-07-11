from policyengine_us.model_api import *


class va_age_deduction_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia adjusted gross income for the age deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",  # § 58.1-322.03.(5)(b)
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=17",
    ]
    defined_for = StateCode.VA

    adds = ["adjusted_gross_income"]
    subtracts = ["tax_unit_taxable_social_security"]
