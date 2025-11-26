from policyengine_us.model_api import *


class ar_additional_tax_credit_for_qualified_individuals(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas additional tax credit for qualified individuals"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    adds = ["ar_additional_tax_credit_for_qualified_individuals_person"]
