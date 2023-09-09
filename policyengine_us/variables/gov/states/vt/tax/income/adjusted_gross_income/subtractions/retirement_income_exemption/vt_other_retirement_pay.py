from policyengine_us.model_api import *


class vt_other_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "Vermont allowed other system's retirement income"
    unit = USD
    definition_period = YEAR
    documentation = "Retirement income from Vermont allowed certain other retirement systems."
    reference = "https://tax.vermont.gov/individuals/seniors-and-retirees"  # Exemption for Other Eligible Retirement Systems
