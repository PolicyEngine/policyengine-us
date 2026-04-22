from policyengine_us.model_api import *


class vt_ccfap_state_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    defined_for = "vt_ccfap_eligible_child"
    label = "Vermont CCFAP state reimbursement rate per child"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-State-Rates.pdf",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Guidance-CCFAP-Capped-Rates.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.ccfap.rates
        provider_type = person("vt_ccfap_provider_type", period)
        care_schedule = person("vt_ccfap_care_schedule", period)
        age_group = person("vt_ccfap_age_group", period)
        is_center = provider_type == provider_type.possible_values.LICENSED_CENTER
        center_rate = p.licensed_center[care_schedule][age_group]
        home_rate = p.registered_home[care_schedule][age_group]
        return where(is_center, center_rate, home_rate)
