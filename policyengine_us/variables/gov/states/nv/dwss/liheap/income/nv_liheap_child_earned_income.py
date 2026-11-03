from policyengine_us.model_api import *


class nv_liheap_child_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP children's earned income"
    documentation = (
        "Earned income of a school-attending household member under 18, "
        "excluded from eligibility income and counted toward the Fixed "
        "Annual Credit."
    )
    defined_for = StateCode.NV
    reference = (
        # PDF pages 46, 57
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=46",
        # PDF pages 46, 57
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=46",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nv.dwss.liheap.income
        # Section 707 N applies to every child in the home, including one
        # excluded from household size.
        child = (person("age", period) < p.child_age_limit) & person(
            "is_in_k12_school", period
        )
        return where(child, person("nv_liheap_earned_income", period), 0)
