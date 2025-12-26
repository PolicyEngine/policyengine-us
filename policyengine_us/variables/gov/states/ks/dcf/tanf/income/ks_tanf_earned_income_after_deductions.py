from policyengine_us.model_api import *


class ks_tanf_earned_income_after_deductions(Variable):
    value_type = float
    entity = Person
    label = "Kansas TANF earned income after deductions"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-111",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7200.htm",
        "https://content.dcf.ks.gov/ees/keesm/implem_memo/2008_0326_TAF_ei_disregard.htm",
    )
    defined_for = StateCode.KS

    def formula(person, period, parameters):
        # Per KEESM 7211 and K.A.R. 30-4-111:
        # Step 1: Deduct $90 work expense per employed person
        # Step 2: Apply 60% disregard to remainder
        #
        # NOTE: Per K.A.R. 30-4-111(b)(2), the 60% disregard does NOT apply
        # when initially establishing or re-establishing TANF eligibility
        # UNLESS the person received TANF in one of the four preceding months.
        # PolicyEngine cannot track benefit history across periods, so we apply
        # the 60% disregard to all applicants.
        p = parameters(
            period
        ).gov.states.ks.dcf.tanf.income.earned_income_disregard
        gross_earned = person("tanf_gross_earned_income", period)
        # Apply $90 work expense (capped at person's gross earned)
        work_expense = min_(gross_earned, p.flat)
        after_work_expense = gross_earned - work_expense
        # Apply 60% disregard to remainder (keep 40%)
        return after_work_expense * (1 - p.rate)
