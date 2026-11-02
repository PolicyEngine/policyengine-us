from policyengine_us.model_api import *


def ky_ktap_dependent_care_share(person, period):
    """Each member's share of the unit's dependent care disregard.

    Per MS 2840 B.2.c, the disregard applies to only one parent's income, so
    it goes to the member with the most gross earnings (split evenly on ties).
    """
    gross_earned = person("tanf_gross_earned_income", period)
    max_earned = person.spm_unit.max(gross_earned)
    is_recipient = (gross_earned == max_earned) & (gross_earned > 0)
    n_recipients = person.spm_unit.sum(is_recipient * 1.0)
    return where(n_recipients > 0, is_recipient / max_(n_recipients, 1), 0)


def ky_ktap_countable_earnings(gross_earned, dependent_care, p, period):
    """Each member's countable earnings under 921 KAR 2:016 Section 5(3).

    Applies the work expense (MS 2840 A), the dependent care disregard
    (MS 2840 B) and the time-limited earned income disregard (MS 2857).
    `p` is `parameters(period).gov.states.ky.dcbs.ktap.income.deductions`.
    """
    after_work_expense = max_(gross_earned - p.work_expense, 0)
    after_dep_care = max_(after_work_expense - dependent_care, 0)
    # Uses calendar month as proxy for participation months.
    eid_rate = p.earned_income_disregard_rate.calc(period.start.month)
    if p.earned_income_flat_disregard_in_effect:
        flat = p.earned_income_flat_disregard
        remainder = max_(after_dep_care - flat, 0)
        disregard = flat + eid_rate * remainder
    else:
        disregard = eid_rate * after_dep_care
    return max_(after_dep_care - disregard, 0)
