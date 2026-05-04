from policyengine_us.model_api import *


class mn_msa_guardian_fee(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid guardian or conservator fee allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mn.html",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 5(d) and CM 0023.15, the fee
        # shall not exceed five percent of the assistance unit's gross
        # monthly income up to a maximum of $100 per month. Gross income
        # uses the standard CM 0017 / 0019 definition: earned + unearned
        # excluding the SSI payment itself per the SSI-exclusion list.
        # Aggregate to the marital unit before applying the cap.
        p = parameters(period).gov.states.mn.dhs.msa.special_needs.guardian_fee
        has_guardian = person("mn_msa_has_guardian", period)
        gross = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_unearned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        unit_gross = person.marital_unit.sum(gross)
        unit_fee = min_(unit_gross * p.rate, p.max_amount)
        return has_guardian * unit_fee
