from policyengine_us.model_api import *


class is_snap_abawd_discretionary_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Exempt from the SNAP ABAWD time limit via a state discretionary exemption"
    documentation = (
        "State agencies may exempt individuals from the Able-Bodied Adult "
        "Without Dependents (ABAWD) time limit up to a monthly average share "
        "of covered individuals under 7 U.S.C. 2015(o)(6) (8 percent from "
        "fiscal year 2024, previously 15 and then 12 percent). These "
        "exemptions are individually assigned by state caseworkers and are "
        "unobservable in survey data, so this input defaults to false and is "
        "intended to be assigned at data-construction time (e.g., in "
        "populace) among covered individuals."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#o_6",
        "https://www.law.cornell.edu/cfr/text/7/273.24#g",
    )
