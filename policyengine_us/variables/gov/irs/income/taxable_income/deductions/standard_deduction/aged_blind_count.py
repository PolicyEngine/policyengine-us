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
        aged_head = tax_unit("aged_head", period).astype(int)
        aged_spouse = tax_unit("aged_spouse", period).astype(int)
        return blind_head + blind_spouse + aged_head + aged_spouse
