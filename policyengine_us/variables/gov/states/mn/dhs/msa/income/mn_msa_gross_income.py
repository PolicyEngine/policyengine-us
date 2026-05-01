from policyengine_us.model_api import *


class mn_msa_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid gross income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 1, MSA's gross-income screen
        # applies to total earned + unearned income (including SSI itself
        # for the SSI track). Spousal deeming is handled via the SSI
        # deemed-income variables.
        return add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_unearned_income",
                "ssi",
                "ssi_earned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
