from policyengine_us.model_api import *


class ma_tafdc_partially_disregarded_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) partially disregarded earned income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281",
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275",  # (A)
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500",  # (A)
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        work_related_deduction = person(
            "ma_tafdc_work_related_expense_deduction", period
        )
        p = parameters(period).gov.states.ma.dta.tcap.tafdc.earned_income_disregard

        gross_earned_income = person("ma_tcap_gross_earned_income", period)
        earned_income_after_work_related_deduction = max_(
            0, gross_earned_income - work_related_deduction
        )
        earned_income_after_disregard = (
            earned_income_after_work_related_deduction * p.percentage
        )
        # Per 106 CMR 704.275(A), the dependent care deduction is made after the
        # 50% disregard and is the unit's actual expenditure up to the maximum,
        # so it is subtracted once from the unit's earnings. 106 CMR 704.500(A)
        # Steps 2-4 apply the work expense and the 50% disregard to each
        # member, then the dependent care deduction, then total the members'
        # countable earned income. The deduction is allocated to each member in
        # proportion to the member's share of the unit's earnings after the 50%
        # disregard, so the members' amounts add up to the unit's earnings after
        # the disregard less the deduction (not less than zero).
        dependent_care_deduction = person.spm_unit(
            "ma_tafdc_dependent_care_deduction", period
        )
        unit_earned_income_after_disregard = person.spm_unit.sum(
            earned_income_after_disregard
        )
        share = np.divide(
            earned_income_after_disregard,
            unit_earned_income_after_disregard,
            out=np.zeros_like(earned_income_after_disregard, dtype=float),
            where=unit_earned_income_after_disregard > 0,
        )
        return max_(
            0,
            earned_income_after_disregard - dependent_care_deduction * share,
        )
