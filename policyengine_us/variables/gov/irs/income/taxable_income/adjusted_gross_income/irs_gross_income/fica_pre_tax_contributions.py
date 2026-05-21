from policyengine_us.model_api import *


class fica_pre_tax_contributions(Variable):
    value_type = float
    entity = Person
    label = "FICA pre-tax contributions"
    unit = USD
    documentation = (
        "Pre-tax contributions that reduce the FICA wage base (Section 125 items only)."
    )
    definition_period = YEAR
    adds = "gov.irs.gross_income.fica_pre_tax_contributions"
    reference = "IRC §3121(a)"
