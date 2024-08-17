from policyengine_us.model_api import *


def create_personal_credit() -> Reform:
    class personal_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Personal Credit"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            earned_income = tax_unit("tax_unit_earned_income", period)
            unit_size = tax_unit("tax_unit_size", period)
            p = parameters(period).gov.contrib.personal_credit
            phase_in_rate = p.phase_in_rate * unit_size
            earnings_fraction = earned_income * phase_in_rate
            base_amount = p.amount * 4  # Quarterly amount converted to yearly
            return min_(base_amount, earnings_fraction)

    class income_tax_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal non-refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            previous_credits = add(tax_unit, period, p.non_refundable)
            personal_credit = tax_unit("personal_credit", period)
            return previous_credits + personal_credit

    class reform(Reform):
        def apply(self):
            self.neutralize_variable("standard_deduction")
            self.neutralize_variable("eitc")
            self.neutralize_variable("ctc")
            self.update_variable(income_tax_non_refundable_credits)
            self.add_variable(personal_credit)

    return reform


def create_personal_credit_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_personal_credit()

    p = parameters(period).gov.contrib.personal_credit

    if p.in_effect:
        return create_personal_credit()
    else:
        return None


personal_credit = create_personal_credit_reform(None, None, bypass=True)
