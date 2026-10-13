from policyengine_us.model_api import *


class permanent_disability_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "permanent disability retirement pay"
    unit = USD
    documentation = (
        "Disability pay included in federal adjusted gross income of a person "
        "who retired on disability and was permanently and totally disabled "
        "when they retired: wages or payments in lieu of wages from an "
        "employer's accident or health plan or pension plan. The larger of "
        "total_disability_payments and taxable_disability_benefits, so the "
        "same payments are not counted twice. State disability income "
        "exclusions modelled on former IRC 105(d) apply to it."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sr--2024.pdf#page=3",
        "https://www.revenue.wi.gov/TaxForms2024/2024-Schedule2440Wf.pdf#page=2",
    )

    def formula(person, period, parameters):
        retired_on_total_disability = person("retired_on_total_disability", period)
        disability_pay = max_(
            person("total_disability_payments", period),
            person("taxable_disability_benefits", period),
        )
        return retired_on_total_disability * disability_pay
