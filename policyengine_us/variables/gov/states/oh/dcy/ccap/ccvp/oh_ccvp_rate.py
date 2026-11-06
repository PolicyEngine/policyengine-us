from policyengine_us.model_api import *


class oh_ccvp_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Ohio Child Care Choice Voucher Program monthly payment rate"
    definition_period = MONTH
    defined_for = "oh_ccvp_eligible_child"
    reference = (
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_36.pdf#page=2",
        "https://www.lsc.ohio.gov/assets/legislation/136/hb96/en0/files/hb96-kid-bill-analysis-as-enacted-136th-general-assembly.pdf#page=10",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dcy.ccap.ccvp
        # H.B. 96, Section 423.190, moves the voucher to the Publicly Funded
        # Child Care payment rates by November 1, 2026, without the Step Up to
        # Quality enhancement, so the rate before add-ons applies from then on.
        if p.pfcc_rates_in_effect:
            return person("oh_ccap_base_rate", period)
        provider_type = person("oh_ccap_provider_type", period)
        age_group = person("oh_ccap_child_age_group", period)
        return p.payment[provider_type][age_group]
