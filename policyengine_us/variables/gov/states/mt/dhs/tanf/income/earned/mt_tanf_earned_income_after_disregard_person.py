from policyengine_us.model_api import *


class mt_tanf_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "MT Temporary Assistance for Needy Families (TANF) earned income after disregard per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/tanf602-1jan012018.pdf"
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        gross_earnings = person("mt_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.mt.dhs.tanf.income.deductions

        # MT doesn't have rules for new applicants like DC?
        #enrolled = person.spm_unit("is_tanf_enrolled", period)

        earnings_after_flat_exclusion = max_(
            gross_earnings - p.work_related_expense.amount, 0
        )
        percentage_disregard = (
            earnings_after_flat_exclusion
            * p.earned_income_disregard.percentage
        )

        #encode tanf cash dependent care disregard here too?

        return max_(earnings_after_flat_exclusion - percentage_disregard, 0)
    
