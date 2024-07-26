from policyengine_us.model_api import *


def create_middle_class_tax_credit() -> Reform:
    class middle_class_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Middle Class Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.congress.gov/bill/116th-congress/senate-bill/4/text"
        )

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.harris.lift.middle_class_tax_credit
            earned_income = add(tax_unit, period, ["earned_income"])
            pell_grant = add(tax_unit, period, ["pell_grant"])
            total_earned_income = earned_income + pell_grant
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            cap = where(joint, p.cap * p.joint_multiplier, p.cap)
            capped_earned_income = min_(total_earned_income, cap)
            agi = tax_unit("adjusted_gross_income", period)

            excess = max_(0, agi - p.phase_out.start[filing_status])
            phase_out_rate = min_(1, excess / p.phase_out.width[filing_status])
            reduction = capped_earned_income * phase_out_rate
            age = tax_unit.members("age", period)
            age_eligible = age >= p.age_threshold
            eligible = tax_unit.any(age_eligible)
            return max_(0, capped_earned_income - reduction) * eligible

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            previous_credits = add(tax_unit, period, p.refundable)
            middle_class_credit = tax_unit("middle_class_tax_credit", period)
            return middle_class_credit + previous_credits

    class reform(Reform):
        def apply(self):
            self.update_variable(middle_class_tax_credit)
            self.update_variable(income_tax_refundable_credits)

    return reform


def create_middle_class_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_middle_class_tax_credit()

    p = parameters(period).gov.contrib.harris.lift.middle_class_tax_credit

    if p.in_effect:
        return create_middle_class_tax_credit()
    else:
        return None


middle_class_tax_credit = create_middle_class_tax_credit_reform(
    None, None, bypass=True
)
