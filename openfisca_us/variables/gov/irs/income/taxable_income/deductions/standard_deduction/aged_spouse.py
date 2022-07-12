from openfisca_us.model_api import *


class aged_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Aged and or blind head and spouse count"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/63#f"

    def formula(tax_unit, period, parameters):
        age_threshold = parameters(
            period
        ).gov.irs.deductions.standard.aged_or_blind.age_threshold
        return tax_unit("age_spouse", period) >= age_threshold
