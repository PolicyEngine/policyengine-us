from policyengine_us.model_api import *


class tax_unit_s1_form1040(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes tax deductions"
    unit = USD
    documentation = "Whether tax unit completes federal Schedule 1, Form 1040, 1040SR, 1040NR, or 1040SP."
    definition_period = YEAR
