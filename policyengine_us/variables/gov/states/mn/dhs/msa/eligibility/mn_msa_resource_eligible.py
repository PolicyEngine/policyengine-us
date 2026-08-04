from policyengine_us.model_api import *


class mn_msa_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Supplemental Aid resource eligible"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.02",
        "https://www.revisor.mn.gov/statutes/cite/256D.425",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
    )

    def formula(person, period, parameters):
        # SSI recipients have already passed the federal $2,000/$3,000
        # resource test. Per § 256P.02 Subd. 2 (applied to MSA via
        # § 256D.425 Subd. 2(b)), the non-SSI $10,000 cap applies to the
        # assistance unit (married couple combined), not per person.
        # We use ssi_countable_resources here as a proxy; § 256P.02 Subd. 2(b)
        # has a narrower personal-property definition (cash, bank accounts,
        # liquid stocks/bonds, non-excluded vehicles, business accounts) but
        # we don't track that breakdown at the moment.
        p = parameters(period).gov.states.mn.dhs.msa.eligibility
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        countable_resources = person("ssi_countable_resources", period.this_year)
        unit_resources = person.marital_unit.sum(countable_resources)
        return receives_ssi | (unit_resources <= p.asset_limit.non_ssi_track)
