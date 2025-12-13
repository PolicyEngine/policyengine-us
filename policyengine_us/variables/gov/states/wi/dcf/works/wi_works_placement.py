from policyengine_us.model_api import *


class WIWorksPlacement(Enum):
    CSJ = "Community Service Job"
    W2_TRANSITION = "W-2 Transition"
    CMC = "Custodial Parent of Infant"
    ARP = "At Risk Pregnancy"
    NONE = "None"


class wi_works_placement(Variable):
    value_type = Enum
    entity = SPMUnit
    label = "Wisconsin Works placement type"
    definition_period = MONTH
    possible_values = WIWorksPlacement
    default_value = WIWorksPlacement.CSJ
    defined_for = StateCode.WI
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/148",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.1_Community_Service_Jobs_(CSJ).htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.dcf.works.placement
        person = spm_unit.members

        # CMC: Custodial Parent of Infant (child <= 8 weeks ≈ 2 months)
        child_age_months = person("monthly_age", period)
        has_infant = spm_unit.any(child_age_months <= p.cmc_infant_age_limit)

        # ARP: At Risk Pregnancy (3rd trimester = month 7+)
        is_pregnant = person("is_pregnant", period)
        pregnancy_month = person("current_pregnancy_month", period)
        in_third_trimester = pregnancy_month >= p.arp_pregnancy_month_threshold
        is_arp_eligible = is_pregnant & in_third_trimester
        has_third_trimester = spm_unit.any(is_arp_eligible)

        # Priority: CMC > ARP > CSJ (W2_T requires agency assessment)
        return select(
            [has_infant, has_third_trimester],
            [WIWorksPlacement.CMC, WIWorksPlacement.ARP],
            default=WIWorksPlacement.CSJ,
        )
