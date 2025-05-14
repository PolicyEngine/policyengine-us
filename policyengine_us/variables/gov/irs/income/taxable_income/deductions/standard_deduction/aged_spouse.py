from policyengine_us.model_api import *


class aged_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Aged spouse"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/63#f"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.standard.aged_or_blind
        return tax_unit("age_spouse", period) >= p.age_threshold
