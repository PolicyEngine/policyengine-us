from policyengine_us.model_api import *


class md_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland military retirement income subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-207",
        # Code letter u, military retirement income.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=17",
        # Filing status 6: a person who can be claimed as a dependent files
        # their own return as a dependent taxpayer.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # § 10-207(a) subtracts amounts only to the extent included in federal
        # AGI. Dependents' income is not in federal AGI; they report it on
        # their own return (Form 502 filing status 6, dependent taxpayer).
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        person_subtraction = person("md_military_retirement_subtraction_amount", period)
        return tax_unit.sum(person_subtraction * head_or_spouse)
