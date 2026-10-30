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
        "https://eohhs.ehs.state.ma.us/DTA/PolicyOnline/BEACON5/%21SSL%21/WebHelp/TAFDC/Employment/Emp_DepCareExTAFDC.htm",
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
        # 50% disregard, and an employed applicant or client receives it for
        # the expenditure on care. 106 CMR 704.500(A) Steps 2-4 apply the work
        # expense and the 50% disregard to each member, then the dependent
        # care deduction, then total the members' countable earned income.
        # The unit's deduction is subtracted once, from the earnings of the
        # member who pays for the care. A part of the deduction above that
        # member's earnings does not reduce another member's earnings. If more
        # than one member is set as a payer, they share the deduction equally.
        dependent_care_deduction = person.spm_unit(
            "ma_tafdc_dependent_care_deduction", period
        )
        payer = person("ma_tafdc_dependent_care_payer", period.this_year)
        payer_count = person.spm_unit.sum(payer)
        share = np.divide(
            payer.astype(float),
            payer_count,
            out=np.zeros_like(earned_income_after_disregard, dtype=float),
            where=payer_count > 0,
        )
        return max_(
            0,
            earned_income_after_disregard - dependent_care_deduction * share,
        )
