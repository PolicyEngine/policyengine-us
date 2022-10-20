from policyengine_us.model_api import *


class aged_blind_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Aged and or blind head and spouse count"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/63#f"

    def formula(tax_unit, period, parameters):
        blind_head = tax_unit("blind_head", period).astype(int)
        blind_spouse = tax_unit("blind_spouse", period).astype(int)
        age_threshold = parameters(
            period
        ).gov.irs.deductions.standard.aged_or_blind.age_threshold
        aged_head = (tax_unit("age_head", period) >= age_threshold).astype(int)
        aged_spouse = (tax_unit("age_spouse", period) >= age_threshold).astype(
            int
        )
        return blind_head + blind_spouse + aged_head + aged_spouse
