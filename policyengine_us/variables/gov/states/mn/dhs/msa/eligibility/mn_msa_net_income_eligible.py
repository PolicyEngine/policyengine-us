from policyengine_us.model_api import *


class mn_msa_net_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Supplemental Aid net income eligible"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 1, MSA pays only to recipients
        # whose countable income is at or below the assistance standard
        # for their living arrangement.
        countable_income = person("mn_msa_countable_income", period)
        standard = person("mn_msa_assistance_standard", period)
        return countable_income <= standard
