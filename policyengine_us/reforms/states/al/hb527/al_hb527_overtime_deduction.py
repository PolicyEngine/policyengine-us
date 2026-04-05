from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_al_hb527_overtime_deduction() -> Reform:
    class al_hb527_overtime_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Alabama HB527 overtime compensation deduction"
        unit = USD
        definition_period = YEAR
        reference = "https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2026RS/HB527-int.pdf#page=9"
        defined_for = StateCode.AL

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.al.hb527
            person = tax_unit.members
            # Use federal FLSA overtime premium calculation per 29 USC 207
            overtime_income = person("fsla_overtime_premium", period)
            # Cap at per-taxpayer limit per AL HB527 Section 40-18-15(a)(29)
            person_capped = min_(overtime_income, p.cap)
            return tax_unit.sum(person_capped)

    class al_agi(Variable):
        value_type = float
        entity = TaxUnit
        label = "Alabama adjusted gross income"
        defined_for = StateCode.AL
        unit = USD
        definition_period = YEAR
        reference = "https://alison.legislature.state.al.us/files/pdf/SearchableInstruments/2026RS/HB527-int.pdf#page=9"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.al.hb527
            # Get the base AL AGI using adds/subtracts
            # NOTE: This mirrors baseline al_agi calculation - update if baseline changes
            gross_sources = parameters(
                period
            ).gov.states.al.tax.income.agi.gross_income_sources
            deductions = parameters(period).gov.states.al.tax.income.agi.deductions
            gross_income = add(tax_unit, period, gross_sources)
            agi_deductions = add(tax_unit, period, deductions)
            base_al_agi = gross_income - agi_deductions
            # If HB527 is in effect, subtract the overtime deduction
            overtime_deduction = tax_unit("al_hb527_overtime_deduction", period)
            return max_(0, base_al_agi - overtime_deduction)

    class reform(Reform):
        def apply(self):
            self.update_variable(al_hb527_overtime_deduction)
            self.update_variable(al_agi)

    return reform


def create_al_hb527_overtime_deduction_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_al_hb527_overtime_deduction()

    p = parameters.gov.contrib.states.al.hb527

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_al_hb527_overtime_deduction()
    else:
        return None


al_hb527_overtime_deduction = create_al_hb527_overtime_deduction_reform(
    None, None, bypass=True
)
