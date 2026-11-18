from policyengine_us.model_api import *


class permanent_disability_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "permanent disability retirement pay"
    unit = USD
    documentation = (
        "Disability income of a person who retired on disability and was "
        "permanently and totally disabled when they retired: "
        "total_disability_payments, the taxable wages or payments in lieu of "
        "wages from an employer's plan that provides for disability "
        "retirement. Payments from a plan without disability retirement are "
        "not disability income, so taxable_disability_benefits alone does not "
        "qualify. State disability income exclusions modelled on former IRC "
        "105(d) apply to it."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sr--2024.pdf#page=3",
        "https://www.revenue.wi.gov/TaxForms2024/2024-Schedule2440Wf.pdf#page=2",
    )

    def formula(person, period, parameters):
        retired_on_total_disability = person("retired_on_total_disability", period)
        disability_income = person("total_disability_payments", period)
        # total_disability_payments is already the taxable amount; as a
        # consistency check it cannot exceed the wages and taxable
        # disability benefits it is reported in.
        included_in_agi = add(
            person, period, ["irs_employment_income", "taxable_disability_benefits"]
        )
        return retired_on_total_disability * max_(
            0, min_(disability_income, included_in_agi)
        )
