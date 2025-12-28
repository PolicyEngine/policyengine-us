from policyengine_us.model_api import *


class hi_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/",
        "http://www.hawaii.edu/bridgetohope/downloads/UPDATED%20STANDARD%20OF%20ASSISTANCE%20AND%20DESK%20AID%20%20EFF.%2001-01-20%202.pdf",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf

        unit_size = spm_unit.nb_persons()
        capped_size = min_(unit_size, p.max_unit_size)

        # Use reduced SOA (80% of full SOA) for work-eligible households
        # NOTE: 20% reduction applies after first 2 months of assistance
        # PolicyEngine cannot track months, so reduced rate is used as default
        return p.standard_of_assistance.reduced.amount[capped_size]
