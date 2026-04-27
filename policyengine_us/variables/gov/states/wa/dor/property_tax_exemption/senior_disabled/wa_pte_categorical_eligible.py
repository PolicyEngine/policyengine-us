from policyengine_us.model_api import *


class wa_pte_categorical_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Categorically eligible for the Washington Senior Citizens and Disabled Persons Property Tax Exemption"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=1",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        # We don't track "retired due to disability" at the moment;
        # use SSDI receipt as a proxy.
        ssdi = person("social_security_disability", period)
        p = parameters(period).gov.states.wa.dor.property_tax_exemption.senior_disabled
        return (age >= p.age_threshold) | (ssdi > 0)
