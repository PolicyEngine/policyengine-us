from policyengine_us.model_api import *
import numpy as np


class ia_basic_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa basic tax is the smaller of regular and alternate taxes"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        regular_tax = tax_unit("ia_regular_tax", period)
        alternate_tax = tax_unit("ia_alternate_tax", period)
        return min_(regular_tax, alternate_tax)
