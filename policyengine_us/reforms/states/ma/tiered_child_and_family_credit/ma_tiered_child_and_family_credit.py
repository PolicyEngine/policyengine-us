from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ma_tiered_child_and_family_credit() -> Reform:
    """Massachusetts tiered Child and Family Tax Credit reform.

    Replaces the flat per-dependent amount with:
    - An age-bracketed amount for dependent children
    - A separate amount for dependent full-time college students under an
      age limit
    - A combined amount for disabled dependents, dependents at or above the
      elderly age limit, and a spouse incapable of self-care

    Eligibility otherwise follows current law: dependents only (plus the
    joint-return self-care spouse), and married-filing-separately filers
    cannot claim the credit.
    """

    class ma_child_and_family_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Massachusetts tiered child and family tax credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.mass.gov/info-details/massachusetts-child-and-family-tax-credit"
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ma.tiered_child_and_family_credit
            p_base = parameters(
                period
            ).gov.states.ma.tax.income.credits.child_and_family
            person = tax_unit.members
            dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            child_amount = p.child_amount.calc(age)
            # Dependent full-time college students under the age limit
            # receive the student amount; students inside the child age
            # brackets receive the greater of the two.
            student = person("is_full_time_college_student", period) & (
                age < p.student_age_limit
            )
            student_amount = student * p.student_amount
            # Disabled dependents at any age (including those incapable of
            # self-care, per IRC Section 21(b)(1)(B)) and dependents at or
            # above the elderly age limit receive the disabled or elderly
            # amount.
            disabled = person("is_disabled", period)
            incapable = person("is_incapable_of_self_care", period)
            elderly = age >= p_base.elderly_age_limit
            disabled_or_elderly = disabled | incapable | elderly
            disabled_or_elderly_amount = (
                disabled_or_elderly * p.disabled_or_elderly_amount
            )
            # Each dependent receives the highest applicable tier.
            per_dependent = max_(
                max_(child_amount, student_amount),
                disabled_or_elderly_amount,
            )
            dependent_total = tax_unit.sum(dependent * per_dependent)
            # A spouse incapable of self-care is a qualifying individual
            # under IRC Section 21(b)(1)(C) on a joint return, following
            # the baseline credit.
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            filing_status = tax_unit("ma_filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            has_self_care_spouse = (
                p_base.disabled_spouse_eligible
                & joint
                & tax_unit.any(head_or_spouse & incapable)
            )
            spouse_total = has_self_care_spouse * p.disabled_or_elderly_amount
            # Married taxpayers filing separately cannot claim the credit.
            separate = filing_status == filing_status.possible_values.SEPARATE
            return ~separate * (dependent_total + spouse_total)

    class reform(Reform):
        def apply(self):
            self.update_variable(ma_child_and_family_credit)

    return reform


def create_ma_tiered_child_and_family_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ma_tiered_child_and_family_credit()

    p = parameters.gov.contrib.states.ma.tiered_child_and_family_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ma_tiered_child_and_family_credit()
    else:
        return None


ma_tiered_child_and_family_credit = create_ma_tiered_child_and_family_credit_reform(
    None, None, bypass=True
)
