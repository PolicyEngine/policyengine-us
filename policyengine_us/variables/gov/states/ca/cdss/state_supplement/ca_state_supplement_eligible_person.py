from policyengine_us.model_api import *


class ca_state_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California SSI state supplement eligible person"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = (
        "https://law.justia.com/codes/california/code-wic/division-9/part-3/chapter-3/article-4/",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.state_supplement.payment_standard
        meets_resource_test = person("meets_ssi_resource_test", period)
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        is_qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period.this_year)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        # Heads and spouses get the individual, couple and facility amounts.
        # The model pays blind or disabled dependents below the age limit the
        # dependent amount instead. This simplifies POMS SI 01415.058, which
        # pays blind children the blind amount, children in care facilities
        # the facility amount and adult dependents an individual amount
        # (issue 10557).
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        dependent = person("is_tax_unit_dependent", period)
        minor = person("monthly_age", period) < p.dependent.age_limit
        return (
            meets_resource_test
            & aged_blind_disabled
            & (is_qualified_noncitizen | is_citizen)
            & (is_head_or_spouse | (dependent & minor))
        )
