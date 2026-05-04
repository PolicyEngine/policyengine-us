from policyengine_us.model_api import *


class mn_msa_representative_payee_fee(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid representative payee fee allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=7",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 5 and Combined Manual 0023.21,
        # MSA pays the SSA standard representative-payee fee to recipients
        # who use a representative payee. This input defaults to false; we
        # do not model detailed representative-payee eligibility.
        p = parameters(period).gov.states.mn.dhs.msa.special_needs
        uses_payee = person("mn_msa_uses_representative_payee", period)
        return uses_payee * p.representative_payee_fee.amount
