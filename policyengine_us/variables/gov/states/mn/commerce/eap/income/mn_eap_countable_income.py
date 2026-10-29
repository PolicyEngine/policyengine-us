from policyengine_us.model_api import *


class mn_eap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Minnesota EAP annual countable income"
    defined_for = StateCode.MN
    reference = (
        # PDF pages 88-102, 107-108, 110-111
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=88",
        # PDF pages 90-103, 109-110, 112-113, 116
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=90",
        "https://www.rrb.gov/RB30/DeductionsforOtherFederalPrograms/MedicareCoverage",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.commerce.eap.income
        person = spm_unit.members
        age = person("age", period)
        # Gross income for one calendar month (prior-year self-employment
        # profit / 12) is approximated by annual inputs; the eligibility test
        # compares the annual total with 12 times the monthly limit.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unemployment = max_(person("total_unemployment_compensation", period), 0)
        # Earnings and unemployment insurance of a person aged 19 or below in
        # K-12, a diploma-granting or an equivalency program are not counted.
        # is_in_k12_school does not identify equivalency programs.
        student = (age <= p.student_age_limit) & person("is_in_k12_school", period)
        earned_and_unemployment = where(student, 0, earned + unemployment)
        unearned = 0
        for source in p.sources.unearned:
            # ADD sums monthly sources such as ssi over the year.
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # Retirement payments count from age 59 1/2. Early benefits before that
        # age count only when not penalized; no input shows whether a withdrawal
        # was penalized, so the age cut-off approximates the penalty test.
        distributions = where(
            age >= p.retirement_age,
            max_(person("retirement_distributions", period), 0),
            0,
        )
        # Social Security and railroad retirement count net of the Medicare
        # premiums withheld from the check, and a pension (PERA) net of Medicare
        # paid out of it. Part A and Part B premiums are subtracted once from the
        # combined amount; Social Security and railroad annuitants have
        # premium-free Part A. No Part D premium input exists.
        social_security = max_(person("social_security", period), 0)
        pension = max_(person("pension_income", period), 0)
        railroad = max_(person("railroad_benefits", period), 0)
        premiums = add(
            person, period, ["medicare_part_a_premium", "medicare_part_b_premium"]
        )
        net_retirement_benefits = max_(
            social_security + pension + railroad - premiums, 0
        )
        person_income = spm_unit.sum(
            earned_and_unemployment + unearned + distributions + net_retirement_benefits
        )
        # Dividends, interest and royalties count only when the one-month
        # equivalent is at least $50; cash gifts only when they total at least
        # $100 in the eligibility month. Royalties have no separate input.
        investment = 0
        for source in p.sources.investment:
            investment = investment + spm_unit.sum(max_(person(source, period), 0))
        counted_investment = where(
            investment / MONTHS_IN_YEAR >= p.investment_minimum, investment, 0
        )
        gifts = spm_unit.sum(max_(person("financial_assistance", period), 0))
        counted_gifts = where(gifts / MONTHS_IN_YEAR >= p.gift_minimum, gifts, 0)
        # MFIP cash is part of tanf. The Diversionary Work Program, MFIP
        # housing assistance grants, Housing Support, tribal per capita payments,
        # irregular income, jury pay, inheritances and lump sums have no input.
        # Child support, capital gains, student aid, Minnesota Supplemental Aid,
        # foster care, tax refunds and SNAP are not counted.
        tanf = max_(spm_unit("tanf", period), 0)
        return person_income + counted_investment + counted_gifts + tanf
