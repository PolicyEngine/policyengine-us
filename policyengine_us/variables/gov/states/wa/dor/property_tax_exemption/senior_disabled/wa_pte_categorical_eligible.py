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
        # The statute requires being "retired from regular gainful employment
        # by reason of disability" (RCW 84.36.381(3)(a)(ii)). We use is_disabled
        # as a proxy — it captures unable-to-work disability across SSDI, SSI,
        # VA, and physician-certified pathways, but doesn't directly verify the
        # "retired from gainful employment" condition.
        is_disabled = person("is_disabled", period)
        p = parameters(period).gov.states.wa.dor.property_tax_exemption.senior_disabled
        return (age >= p.age_threshold) | is_disabled
