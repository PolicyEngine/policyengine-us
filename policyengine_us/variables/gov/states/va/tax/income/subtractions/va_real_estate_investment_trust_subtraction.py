from policyengine_us.model_api import *


class va_real_estate_investment_trust_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Real Estate Investment Trust subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
        "§ 58.1-322.02.(28.a.)",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=28",
    )
    defined_for = StateCode.VA
