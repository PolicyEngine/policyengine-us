from policyengine_us.model_api import *


class ky_ssp_payment_standard(Variable):
    value_type = float
    entity = Person
    label = "Kentucky SSP payment standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLV.pdf#page=5",
    )

    def formula(person, period, parameters):
        # 921 KAR 2:015 §9: per-person standard of need by category, claim
        # type, and (for CARETAKER) whether one or both spouses receive care.
        # Parameter stores per-person values — see payment_standard.yaml.
        category = person("ky_ssp_category", period)
        claim_type = person("ky_ssp_claim_type", period)
        care_receivers = person("ky_ssp_care_receivers", period)
        p = parameters(period).gov.states.ky.dcbs.ssp.payment_standard
        return p[category][claim_type][care_receivers]
