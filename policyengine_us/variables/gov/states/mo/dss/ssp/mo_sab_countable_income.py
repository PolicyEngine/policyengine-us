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
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-20/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-05/0410-015-05-25/",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0410-000-00/0410-015-00/0410-015-15/",
        "https://www.law.cornell.edu/uscode/text/42/1202#a_8",
    )

    def formula(person, period, parameters):
        # 13 CSR 40-2.120(2)(B) counts all of the claimant's own income and
        # another household member's income only in the amount actually made
        # available, so there is no SSI spousal deeming. Appendix K likewise
        # calculates the SAB income test individually, regardless of marital
        # status.
        p = parameters(period).gov.states.mo.dss.ssp.sab.income
        # The Standard Earned Income Exemption Table holds all SAB earned
        # income exemptions: the first $85 plus half the remainder, federal
        # and state income tax, Social Security tax, and a 10% personal
        # standard. It has no SSI student earned income exclusion.
        gross_earned = max_(person("ssi_earned_income", period), 0)
        earned_after_exemption = max_(gross_earned - p.earned_exemption.amount, 0) * (
            1 - p.earned_exemption.rate
        )
        # Allowable taxes, including mandatory city earnings tax paid, are
        # supplied per person and month.
        taxes = person("mo_sab_tax_exemption", period)
        personal_standard = gross_earned * p.personal_standard_rate
        # Court-ordered alimony and child support the claimant pays are
        # expenses of producing income, allowed after the standard exemptions
        # (§ 0410.015.05.25). Garnished wages are also allowed but not modeled.
        expenses = add(person, period, p.expenses_of_producing_income)
        countable_earned = max_(
            earned_after_exemption - taxes - personal_standard - expenses, 0
        )
        # SAB has no general income disregard, so unearned income counts in
        # full. In-kind income such as food or shelter is excluded under
        # § 0410.015.15, and SSI is not income for the need test under
        # § 0410.020.00; ssi_unearned_income includes neither.
        unearned = max_(person("ssi_unearned_income", period), 0)
        return countable_earned + unearned
