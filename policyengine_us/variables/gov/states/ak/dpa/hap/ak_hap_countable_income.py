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
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3003/3003-6_guidelines_for_computing_income.htm",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.hap.income
        person = spm_unit.members
        # Annual inputs approximate prior-month receipts and the alternative
        # seasonal/business annualization rules. Include income of all members,
        # regardless of whether immigration status permits counting their size.
        school = person("is_in_k12_school", period) | person(
            "is_in_secondary_school", period
        )
        # Dependency and schooling approximate parental control and at least
        # half-time elementary/high-school/GED attendance; those details are
        # not separately observed. This exclusion applies only to earnings.
        exempt_child = (
            (person("age", period) < p.child_earnings_age_limit)
            & person("is_tax_unit_dependent", period)
            & school
        )
        # Supplied signed net business income approximates gross receipts less
        # allowable current costs. Do not deduct the 50% expense standard again.
        # Prior-period losses, disallowed tax expenses and multiple businesses
        # within a source cannot be separated. Partnership/S-corp metadata is
        # broader than policy net income; no expense reconstruction is imputed.
        earned = max_(person("employment_income", period), 0) + add(
            person, period, p.business_sources
        )
        countable_earned = spm_unit.sum(where(exempt_child, 0, earned))
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
        # constant monthly rate. The manual excludes strictly under $20 per
        # person per month; annual data cannot identify irregular receipt dates.
        countable_gifts = spm_unit.sum(
            where(gifts / MONTHS_IN_YEAR < p.gift_exemption_threshold, 0, gifts)
        )
        # Reported support represents retained receipts; assignment/payment
        # routes are unavailable, so no ATAP pass-through cap is imputed.
        # Gross SSA includes Medicare withholding. No general medical, care,
        # support-paid or earned-income deduction is authorized by these rules.
        # Count the takeup-sensitive ATAP receipt once per SPM unit.
        total = (
            countable_earned
            + unearned
            + rental
            + countable_gifts
            + spm_unit("tanf", period)
        )
        return max_(total, 0)
