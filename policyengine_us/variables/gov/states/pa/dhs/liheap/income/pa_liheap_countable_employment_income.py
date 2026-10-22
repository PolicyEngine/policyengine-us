from policyengine_us.model_api import *


class pa_liheap_countable_employment_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP countable employment income"
    defined_for = StateCode.PA
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=53",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=50",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.liheap.income
        dependent_child = (person("age", period) < p.child_age_limit) & person(
            "is_tax_unit_dependent", period
        )
        # Section 601.84(21) excludes dependent children's wages, not their
        # business or unearned income. Tax dependency approximates dependency.
        wages = max_(person("employment_income", period), 0)
        return where(dependent_child, 0, wages)
