from policyengine_us.model_api import *


class railroad_benefits_overpayment_withheld(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement annuity withheld to recover overpayments"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Annual amount the Railroad Retirement Board withholds from annuities "
        "to recover past overpayments. Enter only recoveries that the reported "
        "railroad_benefits amount still includes."
    )
    reference = (
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0610-000-00/0610-005-00/"
    )
