from policyengine_us.model_api import *


class medicaid_ltss_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS countable resources"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "LTSS countable resources derived from each person's own resource "
        "inventory. An individual budget uses the applicant's resources; "
        "a couple budget combines both spouses' resources within their "
        "marital unit. Community spouse allowances are applied by the "
        "separate CSRA resource eligibility calculation."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.601",
        "https://www.law.cornell.edu/cfr/text/42/435.602",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67",
    )

    def formula_2026_01_01(person, period, parameters):
        own_resources = person("medicaid_ltss_individual_countable_resources", period)
        return where(
            person("medicaid_ltss_assistance_unit_size", period) == 2,
            person.marital_unit.sum(own_resources),
            own_resources,
        )
