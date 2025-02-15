from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_fisc_act() -> Reform:
    class family_income_supplement_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "FISC Act family income supplement"
        unit = USD
        definition_period = YEAR
        reference = "https://golden.house.gov/sites/evo-subsites/golden.house.gov/files/evo-media-document/GoldenFISC.pdf"

        def formula(tax_unit, period, parameters):

            # Calcualte the base amount
            person = tax_unit.members
            is_pregnant = person("is_pregnant", period)
            is_dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            p = parameters(
                period
            ).gov.contrib.congress.golden.fisc_act.family_income_supplement
            eligible_dependent = (age < p.child_age_threshold) & is_dependent
            pergnant_amount = p.amount.pregnant * is_pregnant
            dependent_amount = p.amount.base.calc(age) * eligible_dependent
            total_base_amount = (
                tax_unit.sum(pergnant_amount + dependent_amount)
                * MONTHS_IN_YEAR
            )
            # A joint bonus is applied to the base amount
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            base_with_bonus = where(
                joint,
                (total_base_amount * p.marriage_bonus_rate)
                + total_base_amount,
                total_base_amount,
            )

            # The credit is capped at a percentage of the total adjusted gross income
            agi = tax_unit("adjusted_gross_income", period)
            agi_threshold = p.income_threshold * agi
            capped_credit = min_(base_with_bonus, agi_threshold)

            # The credit is further reduced by a phase-out rate
            phase_out = where(
                joint, p.phase_out.joint.calc(agi), p.phase_out.other.calc(agi)
            )
            return max_(capped_credit - phase_out, 0)

    def modify_parameters(parameters):
        parameters.gov.irs.credits.refundable.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "eitc",
                "refundable_american_opportunity_credit",
                "recovery_rebate_credit",
                "refundable_payroll_tax_credit",
                "family_income_supplement_credit",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(family_income_supplement_credit)
            self.modify_parameters(modify_parameters)
            self.neutralize_variable("refundable_ctc")
            self.neutralize_variable("non_refundable_ctc")

    return reform


def create_fisc_act_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_fisc_act()

    p = parameters.gov.contrib.congress.golden.fisc_act

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_fisc_act()
    else:
        return None


fisc_act = create_fisc_act_reform(None, None, bypass=True)
