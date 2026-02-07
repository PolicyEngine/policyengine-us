from policyengine_us.model_api import *


class would_file_if_eligible_for_refundable_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "would file taxes if eligible for refundable credit"
    documentation = """
    Whether this tax unit would file taxes if eligible for a refundable tax
    credit (EITC, ACTC, etc.), even if not legally required to file.

    This is an input variable assigned during microdata construction based
    on propensity modeling. The vast majority of refundable credit eligible
    filers do file to claim their credits.
    """
    definition_period = YEAR
    default_value = True
