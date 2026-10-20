from policyengine_us.model_api import *


class ca_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
    defined_for = StateCode.CA
    adds = [
        "ca_hsa_addition",
        "ca_educator_expense_addition",
        "ca_other_additions",
        "ca_out_of_state_municipal_bond_interest",
    ]
