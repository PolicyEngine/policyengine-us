from policyengine_us.model_api import *


class mo_snc_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri SNC countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MO
    documentation = (
        "Approximates Supplemental Nursing Care countable income from modeled "
        "cash sources. Missouri excludes Railroad Retirement overpayment recoveries "
        "from the annuity. The model omits other Missouri-specific exclusions, "
        "overhead expenses and supported employment disregards."
    )
    reference = (
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0610-000-00/0610-005-00/",
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0610-000-00/0610-025-00/",
    )

    def formula(person, period, parameters):
        other_income = add(person, period, ["market_income", "social_security", "ssi"])
        railroad = person("railroad_benefits", period)
        withheld = person("railroad_benefits_overpayment_withheld", period)
        return other_income + max_(railroad - withheld, 0)
