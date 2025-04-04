from policyengine_us.model_api import *


class ma_tafdc_partially_disregarded_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) partially disregarded earned income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # work_related_deduction = person(
        #     "ma_tafdc_work_related_expense_deduction", period
        # )
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.tafdc.earned_income_disregard

        gross_earned_income = person("ma_tcap_gross_earned_income", period)
        earned_income_after_work_related_deduction = max_(
            0, gross_earned_income - 0
        )
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        dependent_care_deduction = person.spm_unit(
            "ma_tafdc_dependent_care_deduction", period
        )
        # Attributing the dependent care deduction equally to each spouse if filing jointly
        applicable_dependent_care_deduction = where(
            joint, dependent_care_deduction / 2, dependent_care_deduction
        )
        return max_(
            0,
            earned_income_after_work_related_deduction * p.percentage
            - applicable_dependent_care_deduction,
        )
