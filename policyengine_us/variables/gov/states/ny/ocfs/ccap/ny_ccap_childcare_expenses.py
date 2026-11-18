from policyengine_us.model_api import *


class ny_ccap_childcare_expenses(Variable):
    value_type = float
    entity = Person
    label = "New York CCAP monthly expenses allocated to the child"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "Allocates family expenses equally among all children in paid care, "
        "including children who do not qualify for CCAP. Each child keeps "
        "their own expense share when applying the market rate and "
        "differentials under 18 NYCRR 415.9."
    )
    reference = "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9"

    def formula(person, period, parameters):
        in_care = person("childcare_hours_per_day", period.this_year) > 0
        children_in_care = person.spm_unit.sum(in_care)
        total = person.spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        return total / max_(children_in_care, 1)
