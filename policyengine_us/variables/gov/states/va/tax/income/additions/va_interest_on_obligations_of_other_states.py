from policyengine_us.model_api import *


class va_interest_on_obligations_of_other_states(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia interest on obligations of other states"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
        "§ 58.1-322.01.(1.)",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=24",
    )
    defined_for = StateCode.VA
