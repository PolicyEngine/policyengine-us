from policyengine_us.model_api import *
from policyengine_us.tools.parameters import add_to_list_parameter


def create_boost_middle_class_tax_credit() -> Reform:
    class boost_middle_class_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "BOOST Middle Class Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://d12t4t5x3vyizu.cloudfront.net/tlaib.house.indigov.us/uploads/2022/05/TLAIB_046_xml.pdf"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.harris.lift.middle_class_tax_credit
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            amount = where(joint, p.cap * p.joint_multiplier, p.cap)
            agi = tax_unit("adjusted_gross_income", period)

            excess = max_(0, agi - p.phase_out.start[filing_status])
            phase_out_rate = min_(1, excess / p.phase_out.width[filing_status])
            reduction = amount * phase_out_rate
            age = tax_unit.members("age", period)
            age_eligible = age >= p.age_threshold
            eligible = tax_unit.any(age_eligible)
            return max_(0, amount - reduction) * eligible

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            previous_credits = add(tax_unit, period, p.refundable)
            middle_class_credit = tax_unit("boost_middle_class_tax_credit", period)
            p_boost = parameters(
                period
            ).gov.contrib.congress.tlaib.boost.middle_class_tax_credit
            if p_boost.administered_through_ssa:
                return previous_credits
            return middle_class_credit + previous_credits

    class boost_middle_class_tax_credit_paid_through_ssa(Variable):
        value_type = float
        entity = TaxUnit
        label = "BOOST Middle Class Tax Credit paid through SSA"
        unit = USD
        definition_period = YEAR
        documentation = (
            "The credit as a benefit when the Social Security Administration "
            "pays it, and zero when it is a refundable income tax credit."
        )

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.boost.middle_class_tax_credit
            credit = tax_unit("boost_middle_class_tax_credit", period)
            return credit * p.administered_through_ssa

    def modify_parameters(parameters):
        # Paid through SSA, the credit is a benefit in both income totals;
        # otherwise income_tax_refundable_credits counts it.
        household = parameters.gov.household
        paid_through_ssa = ["boost_middle_class_tax_credit_paid_through_ssa"]
        add_to_list_parameter(household.household_benefits, paid_through_ssa)
        add_to_list_parameter(household.spm_unit_benefits, paid_through_ssa)
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(boost_middle_class_tax_credit)
            self.update_variable(boost_middle_class_tax_credit_paid_through_ssa)
            self.update_variable(income_tax_refundable_credits)
            self.modify_parameters(modify_parameters)

    return reform


def create_boost_middle_class_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_boost_middle_class_tax_credit()

    p = parameters(period).gov.contrib.harris.lift.middle_class_tax_credit

    if p.in_effect:
        return create_boost_middle_class_tax_credit()
    else:
        return None


boost_middle_class_tax_credit = create_boost_middle_class_tax_credit_reform(
    None, None, bypass=True
)
