from policyengine_us.model_api import *


class mn_msa_categorically_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Supplemental Aid categorically eligible"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 1, MSA covers two paths:
        #   (a) currently receiving SSI (the SSI track), or
        #   (b) categorically SSI-eligible but income-ineligible for SSI,
        #       with countable income at or below the MSA assistance
        #       standard (the non-SSI excess-income track).
        # Both paths require aged/blind/disabled status. The non-SSI
        # track uses the higher state $10,000 resource cap, so we check
        # ABD directly rather than is_ssi_eligible (which includes the
        # federal $2,000 resource test).
        return person("is_ssi_aged_blind_disabled", period.this_year)
