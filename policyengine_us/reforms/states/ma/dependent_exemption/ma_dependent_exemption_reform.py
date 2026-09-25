from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ma_dependent_exemption_reform() -> Reform:
    class ma_part_b_taxable_income_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "MA Part B taxable income exemption"
        unit = USD
        definition_period = YEAR
        reference = "https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemption"
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            tax = parameters(period).gov.states.ma.tax.income
            pc = parameters(period).gov.contrib.states.ma.dependent_exemption
            person = tax_unit.members
            filing_status = tax_unit("ma_filing_status", period)
            # (B)(b): Exemptions.
            # (1A) and (2A): Personal exemption based on filing status.
            personal_exemption = tax.exemptions.personal[filing_status]
            # (1B) and (2B): Blind exemptions.
            blind = person("is_blind", period)
            dependent = person("is_tax_unit_dependent", period)
            count_blind = tax_unit.sum(~dependent & blind)
            blind_exemption = tax.exemptions.blind * count_blind
            # (1C) and (2C): Aged exemptions.
            age = person("age", period)
            count_aged = tax_unit.sum(~dependent & (age >= tax.exemptions.aged.age))
            aged_exemption = tax.exemptions.aged.amount * count_aged
            # (3): Dependent exemptions — the reformed piece. Dependents
            # under the age threshold (all dependents when the age limit is
            # off) take the contrib amount; older dependents keep the
            # baseline per-dependent exemption. Only apply the reform
            # pricing in periods where the reform is in effect — the reform
            # is installed for the whole simulation whenever it activates in
            # any of the next five years, so this per-period gate prevents
            # the reform amount leaking into pre-activation years.
            if pc.in_effect:
                if pc.age_limit.in_effect:
                    young = dependent & (age < pc.age_limit.threshold)
                else:
                    young = dependent
                count_young = tax_unit.sum(young)
                count_older = tax_unit.sum(dependent) - count_young
                if pc.amount < 0:
                    reform_amount = tax.exemptions.dependent
                else:
                    reform_amount = pc.amount
                dependent_exemption = (
                    reform_amount * count_young + tax.exemptions.dependent * count_older
                )
            else:
                count_dependents = tax_unit("tax_unit_dependents", period)
                dependent_exemption = tax.exemptions.dependent * count_dependents
            # (4): Medical expense deduction for itemizers.
            itemizes = tax_unit("tax_unit_itemizes", period)
            federal_medical_expense_deduction = tax_unit(
                "medical_expense_deduction", period
            )
            medical_dental_exemption = itemizes * federal_medical_expense_deduction
            return (
                personal_exemption
                + dependent_exemption
                + aged_exemption
                + blind_exemption
                + medical_dental_exemption
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(ma_part_b_taxable_income_exemption)

    return reform


def create_ma_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ma_dependent_exemption_reform()

    p = parameters.gov.contrib.states.ma.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ma_dependent_exemption_reform()
    else:
        return None


ma_dependent_exemption_reform = create_ma_dependent_exemption_reform_fn(
    None, None, bypass=True
)
