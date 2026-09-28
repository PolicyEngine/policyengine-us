from policyengine_us.model_api import *


class mo_sab_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri SAB countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://revisor.mo.gov/main/OneSection.aspx?section=209.240",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-20/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-25/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-10/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-15/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-020-00/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2018/10/appendix_k.pdf#page=5",
    )

    def formula(person, period, parameters):
        # 13 CSR 40-2.120(2)(B) counts all of the claimant's own income and
        # another household member's income only in the amount actually made
        # available, so there is no SSI spousal deeming. Appendix K likewise
        # calculates the SAB income test individually, regardless of marital
        # status.
        p = parameters(period).gov.states.mo.dss.ssp.sab.income
        # Earned income exemptions (§ 0410.015.05.20): the first $85 plus half
        # the remainder (RSMo 209.240.1), taxes on earnings, and a personal
        # standard of 10% of gross earnings. There is no SSI student exclusion.
        # A self-employment loss offsets wages; total earnings floor at zero.
        gross_earned = max_(add(person, period, p.sources.earned), 0)
        earned_after_exemption = max_(gross_earned - p.earned_exemption.amount, 0) * (
            1 - p.earned_exemption.rate
        )
        # Taxes on earnings are an entered amount. The 13 CSR 40-2.120(8)
        # standard tax table for gross earnings up to $1,200 is not modeled.
        taxes = person("mo_sab_reported_earnings_taxes", period)
        # The 13 CSR table rounds the 10% personal standard up to the top of
        # each $5 band (at most $0.50 more); this follows the manual's 10% of
        # gross earnings. Actual work expenses above the standard are not
        # modeled.
        personal_standard = gross_earned * p.personal_standard_rate
        countable_earned = max_(earned_after_exemption - taxes - personal_standard, 0)
        # SAB has no general income disregard, so unearned income counts in
        # full. In-kind income is excluded under § 0410.015.15, and SSI is not
        # income for the need test under § 0410.020.00.
        unearned = max_(add(person, period, p.sources.unearned), 0)
        # Court-ordered alimony and child support paid are expenses of
        # producing income (§ 0410.015.05.25), which § 0410.015.10 also applies
        # to unearned income. Garnished wages are also allowed but not modeled.
        expenses = add(person, period, p.expenses_of_producing_income)
        return max_(countable_earned + unearned - expenses, 0)
