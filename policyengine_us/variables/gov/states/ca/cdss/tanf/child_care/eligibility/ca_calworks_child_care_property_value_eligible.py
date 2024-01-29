from policyengine_us.model_api import *


class ca_calworks_child_care_property_value_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible child for the California CalWORKs Child Care based on the property value"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://dpss.lacounty.gov/en/cash/calworks.html"

    def formula(spm_unit, period, parameters):
        assets = spm_unit("spm_unit_cash_assets", period)
        # The limit increases if it least one person is aged or disabled
        person = spm_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.child_care.eligibility.resource_limit
        aged = age >= p.property.age_threshold
        has_aged_or_disabled_person = spm_unit.any(aged | disabled)
        value_limit = where(
            has_aged_or_disabled_person,
            p.property.aged_or_disabled,
            p.property.base,
        )
        return assets <= value_limit
