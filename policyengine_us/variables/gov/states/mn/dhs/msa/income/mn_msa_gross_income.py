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
        # applies to total earned + unearned income. For SSI recipients,
        # the county counts the applicable federal SSI benefit rate, not
        # the post-income SSI payment.
        income = add(
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
        ssi = person("ssi", period)
        ssi_fbr = person("ssi_amount_if_eligible", period)
        return income + where(ssi > 0, ssi_fbr, ssi)
