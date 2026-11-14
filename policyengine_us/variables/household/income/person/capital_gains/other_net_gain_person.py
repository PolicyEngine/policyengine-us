from policyengine_us.model_api import *


class other_net_gain_person(Variable):
    value_type = float
    entity = Person
    label = "Other net gain or loss from Form 4797, per person"
    unit = USD
    documentation = (
        "The tax unit's Form 4797 other net gain or loss (other_net_gain), split "
        "equally between the head and spouse, with its sign. Income measures add "
        "it, and other_net_gain_gross_income takes its positive part."
    )
    definition_period = YEAR
    reference = "https://www.irs.gov/instructions/i4797"

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # Head and spouse only, without filing_status: dependent_gross_income
        # reads gross income through this variable, and filing_status depends
        # on dependent_gross_income through head_of_household_eligible.
        is_head_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        filers = tax_unit.sum(is_head_or_spouse)
        share = is_head_or_spouse / max_(filers, 1)
        return share * tax_unit("other_net_gain", period)
