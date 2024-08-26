from policyengine_us.model_api import *



def create_mi_food_assitance_credit() -> Reform:
    class mi_food_assistance_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan food assistance tax credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.legislature.mi.gov/documents/2023-2024/billintroduced/House/pdf/2024-HIB-5628.pdf"
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            exemptions = tax_unit("mi_exemptions", period)
            fpg = tax_unit("tax_unit_fpg", period)
            excess = max_(fpg - exemptions, 0)
            p = parameters(period).gov.contrib.states.mi.food_assistance_credit
            return excess * p.refundable_rate
