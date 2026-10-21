from policyengine_us.model_api import *


class oh_qualifying_capital_gain_deductible_payroll(Variable):
    value_type = float
    entity = Person
    label = "Ohio deductible payroll for the qualifying capital gain deduction"
    documentation = (
        "The qualifying payroll of the entity whose sale produced the "
        "qualifying capital gain, multiplied by the percentage of the entity "
        "the taxpayer sold (R.C. 5747.79(A)(3)-(4))."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.79"
    defined_for = StateCode.OH
