from policyengine_us.model_api import *


class tx_fpp_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Family Planning Program dependent care deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-382-109",
        "https://www.hhs.texas.gov/handbooks/family-planning-program-policy-manual/4100-client-eligibility-screening-process",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.fpp.income
        person = spm_unit.members
        # 1 TAC 382.109(2)(A) covers child dependents ($200 per month
        # under age two, $175 per month otherwise); (2)(B) allows up to
        # $175 per month for each dependent adult with a disability.
        # The FPP policy manual "Income Deductions" section allows
        # "$175 per adult with disabilities per month" with no
        # dependency qualifier, which covers a disabled spouse.
        childcare_expenses = person("pre_subsidy_childcare_expenses", period)
        adult_care_expenses = person("care_expenses", period)
        age = person("age", period)
        is_child = age < p.child_age_threshold
        # is_tax_unit_spouse flags the oldest non-head adult even when
        # unmarried, so require an actual two-person marital unit.
        is_spouse = person("is_tax_unit_spouse", period) & (
            person.marital_unit.nb_persons() == 2
        )
        is_disabled_adult = (
            person("is_disabled", period)
            & ~is_child
            & (person("is_tax_unit_dependent", period) | is_spouse)
        )
        eligible_expenses = (
            childcare_expenses * is_child + adult_care_expenses * is_disabled_adult
        )
        monthly_cap = p.dependent_care.calc(age)
        capped_expenses = min_(eligible_expenses, monthly_cap * MONTHS_IN_YEAR)
        return spm_unit.sum(capped_expenses)
