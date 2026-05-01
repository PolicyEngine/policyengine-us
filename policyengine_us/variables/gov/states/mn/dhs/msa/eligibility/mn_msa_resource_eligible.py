from policyengine_us.model_api import *


class mn_msa_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Supplemental Aid resource eligible"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.37",
        "https://www.lawhelpmn.org/self-help-library/fact-sheet/minnesota-supplemental-aid-msa",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.37: SSI track recipients (ssi > 0) already
        # passed the federal SSI $2,000/$3,000 resource test. The non-SSI
        # excess-income track uses a higher $10,000 personal-property cap.
        p = parameters(period).gov.states.mn.dhs.msa.eligibility
        receives_ssi = person("ssi", period) > 0
        countable_resources = person("ssi_countable_resources", period.this_year)
        non_ssi_track_eligible = countable_resources <= p.asset_limit.non_ssi_track
        return receives_ssi | non_ssi_track_eligible
