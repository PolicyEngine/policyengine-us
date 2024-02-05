from policyengine_us.model_api import *


class va_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia adjusted federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2022/760-2022.pdf",
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
    )
    defined_for = StateCode.VA

    adds = ["adjusted_gross_income", "va_additions"]

    subtracts = ["va_subtractions"]
