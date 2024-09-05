from policyengine_us.model_api import *


def create_mi_food_assitance_credit() -> Reform:
    class mi_food_assistance_fpg_excess(Variable):
        value_type = float
        entity = TaxUnit
        label = "Excess of FPG over the state exemption amount in Michigan for the food assistance tax credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.legislature.mi.gov/documents/2023-2024/billintroduced/House/pdf/2024-HIB-5628.pdf"
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            exemptions = tax_unit("mi_exemptions", period)
            fpg = tax_unit("tax_unit_fpg", period)
            return max_(fpg - exemptions, 0)

    class mi_food_assistance_refundable_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan food assistance refundable tax credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.legislature.mi.gov/documents/2023-2024/billintroduced/House/pdf/2024-HIB-5628.pdf"
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            excess = tax_unit("mi_food_assistance_fpg_excess", period)
            p = parameters(period).gov.contrib.states.mi.food_assistance_credit
            return excess * p.refundable_rate

    class mi_food_assistance_non_refundable_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan food assistance non-refundable tax credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.legislature.mi.gov/documents/2023-2024/billintroduced/House/pdf/2024-HIB-5628.pdf"
        defined_for = StateCode.MI

        adds = ["mi_food_assistance_fpg_excess"]
        subtracts = ["mi_food_assistance_refundable_credit"]

    class mi_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan non-refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MI

        adds = ["mi_food_assistance_non_refundable_credit"]

    class mi_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.mi.tax.income.credits
            previous_credits = add(tax_unit, period, p.refundable)
            food_assistance_credit = tax_unit(
                "mi_food_assistance_refundable_credit", period
            )
            return previous_credits + food_assistance_credit

    class reform(Reform):
        def apply(self):
            self.update_variable(mi_food_assistance_fpg_excess)
            self.update_variable(mi_food_assistance_refundable_credit)
            self.update_variable(mi_food_assistance_non_refundable_credit)
            self.update_variable(mi_non_refundable_credits)
            self.update_variable(mi_refundable_credits)

    return reform


def create_mi_food_assitance_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_mi_food_assitance_credit()

    p = parameters(period).gov.contrib.states.mi.food_assistance_credit

    if p.in_effect:
        return create_mi_food_assitance_credit()
    else:
        return None


mi_food_assistance_credit = create_mi_food_assitance_credit_reform(
    None, None, bypass=True
)
