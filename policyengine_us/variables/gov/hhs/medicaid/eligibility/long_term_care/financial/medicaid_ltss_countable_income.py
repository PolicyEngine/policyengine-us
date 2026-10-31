from policyengine_us.model_api import *


class medicaid_ltss_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS countable income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Income for the selected individual or couple budget after "
        "qualified income trust deposits and modeled state income "
        "exclusions. Each spouse supplies their own gross source amounts; "
        "the model computes the combined budget and its exclusions."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
    )

    def formula_2026_01_01(person, period, parameters):
        return where(
            person("medicaid_ltss_assistance_unit_size", period) == 2,
            person("medicaid_ltss_couple_countable_income", period),
            person("medicaid_ltss_individual_countable_income", period),
        )
