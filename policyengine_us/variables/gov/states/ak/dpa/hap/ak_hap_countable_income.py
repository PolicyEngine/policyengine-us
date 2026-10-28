from policyengine_us.model_api import *


class ak_hap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alaska HAP countable income"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3003/3003-1_countable_income.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3003/3003-2_noncountable_(exempt)_income.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3003/3003-4_income_from_self-employment.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3003/3003-5_military_pay.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3003/3003-6_guidelines_for_computing_income.htm",
        "https://www.akleg.gov/basis/aac.asp?media=print&secStart=7.44.010&secEnd=7.44.9001",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.hap.income
        person = spm_unit.members
        # Annual inputs approximate prior-month receipts and the alternative
        # seasonal/business annualization rules. Include income of all members,
        # regardless of whether immigration status permits counting their size.
        # 7 AAC 44.042(5) exempts wages of a full-time student under 18 who is
        # not the head of household. The tax-unit head stands in for the head
        # of household. is_full_time_student treats any K-12 attendance as
        # full time, since part-time enrollment is not observed. Only wages
        # (employment income and military basic pay) are exempt; the
        # student's business income still counts.
        exempt_student = (
            (person("age", period) < p.child_earnings_age_limit)
            & person("is_full_time_student", period)
            & ~person("is_tax_unit_head", period)
        )
        # Supplied net business income stands in for gross receipts less
        # costs. Manual 3003-4 B deducts 50% of gross unless actual costs are
        # higher, so net inputs overstate countable income when actual costs
        # are under half of gross. Each source is floored at zero, so a
        # business loss does not offset wages or other income. Prior-period
        # losses, disallowed tax expenses and multiple businesses within a
        # source cannot be separated.
        earned = 0
        for source in p.earned_sources:
            earned = earned + max_(person(source, period), 0)
        wages = max_(person("employment_income", period), 0) + max_(
            person("military_basic_pay", period), 0
        )
        countable_earned = spm_unit.sum(earned - where(exempt_student, wages, 0))
        # These are cash receipts, so a tax loss in an unearned source does not
        # offset other income. Net rental sources are separately nonnegative.
        unearned_person = 0
        for source in p.unearned_sources:
            unearned_person = unearned_person + max_(person(source, period), 0)
        unearned = spm_unit.sum(unearned_person)
        rental = spm_unit.sum(
            max_(person("rental_income", period), 0)
            + max_(person("farm_rent_income", period), 0)
        )
        gifts = person("financial_assistance", period)
        # Existing outside cash support approximates gifts received at a
        # constant monthly rate. 7 AAC 44.042(16) exempts gifts that do not
        # exceed $20 per person per month, and manual 3003-1 B.6.r counts
        # gifts over $20; annual data cannot identify irregular receipt dates.
        countable_gifts = spm_unit.sum(
            where(gifts / MONTHS_IN_YEAR <= p.gift_exemption_threshold, 0, gifts)
        )
        # Reported support represents retained receipts; assignment/payment
        # routes are unavailable, so no ATAP pass-through cap is imputed.
        # Gross SSA includes Medicare withholding. No general medical, care,
        # support-paid or earned-income deduction is authorized by these rules.
        # Count the takeup-sensitive ATAP receipt once per SPM unit.
        return (
            countable_earned
            + unearned
            + rental
            + countable_gifts
            + spm_unit("tanf", period)
        )
