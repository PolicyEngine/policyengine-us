from policyengine_us.model_api import *
import numpy as np


class ia_basic_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa basic tax is smaller of base+AMT taxes for indiv and joint"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        basic_indiv = add(
            tax_unit, period, ["ia_base_tax_indiv", "ia_amt_indiv"]
        )
        basic_joint = add(
            tax_unit, period, ["ia_base_tax_joint", "ia_amt_joint"]
        )
        return min_(basic_indiv, basic_joint)
