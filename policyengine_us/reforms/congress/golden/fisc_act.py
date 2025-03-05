from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_fisc_act() -> Reform:
    class family_income_supplement_credit_base_amount(Variable):
        value_type = float
        entity = Person
        label = "FISC Act family income supplement base amount"
        unit = USD
        definition_period = YEAR
        reference = "https://golden.house.gov/sites/evo-subsites/golden.house.gov/files/evo-media-document/GoldenFISC.pdf"

        def formula(person, period, parameters):
            # Calculate the base amount
            is_dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            p = parameters(
                period
            ).gov.contrib.congress.golden.fisc_act.family_income_supplement
            eligible_dependent = (age < p.child_age_limit) & is_dependent
            return p.amount.base.calc(age) * eligible_dependent

    class family_income_supplement_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "FISC Act family income supplement"
        unit = USD
        definition_period = YEAR
        reference = "https://golden.house.gov/sites/evo-subsites/golden.house.gov/files/evo-media-document/GoldenFISC.pdf"

        def formula(tax_unit, period, parameters):

            p = parameters(
                period
            ).gov.contrib.congress.golden.fisc_act.family_income_supplement
            # A joint bonus is applied to the base amount
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            base_amount = add(
                tax_unit,
                period,
                [
                    "family_income_supplement_credit_base_amount",
                ],
            )
            base_amount_with_marriage_bonus = base_amount * (
                1 + joint * p.marriage_bonus_rate
            )
            agi = tax_unit("adjusted_gross_income", period)
            phase_out = where(
                joint, p.phase_out.joint.calc(agi), p.phase_out.other.calc(agi)
            )
            phased_out_amount = max_(
                base_amount_with_marriage_bonus - phase_out, 0
            )
            agi_threshold = max_(0, p.agi_fraction * agi)
            capped_credit = min_(phased_out_amount, agi_threshold)
            # The credit is limited to eligible caregivers
            person = tax_unit.members
            age = person("age", period)
            age_eligible = age >= p.caregiver_age_threshold
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            eligible_caregiver_present = tax_unit.any(
                age_eligible & head_or_spouse
            )
            return capped_credit * eligible_caregiver_present

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
            self.update_variable(family_income_supplement_credit_base_amount)
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
