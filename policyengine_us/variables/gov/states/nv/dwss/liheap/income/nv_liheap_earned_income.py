from policyengine_us.model_api import *


class nv_liheap_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP earned income"
    documentation = (
        "Annual gross earned income of a household member, before the "
        "children's earned income exclusion from eligibility income."
    )
    defined_for = StateCode.NV
    reference = (
        # PDF pages 43-44, 46-48
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=43",
        # PDF pages 43-44, 46-48
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=43",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nv.dwss.liheap.income
        # Annual inputs stand in for the 30-day income annualized under
        # Section 804. Each source is floored at zero, so a loss in one
        # source cannot offset another.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        return earned
