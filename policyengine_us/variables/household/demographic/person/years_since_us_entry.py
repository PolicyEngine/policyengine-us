from policyengine_us.model_api import *


class years_since_us_entry(Variable):
    value_type = float
    entity = Person
    label = "Years since US entry or qualified immigration status grant"
    unit = "year"
    definition_period = YEAR
    default_value = 5
    # 8 USC 1613(a) defines the federal five-year limited eligibility
    # period. The default of 5 here is a PolicyEngine modeling decision —
    # not a statutory value — chosen to treat unspecified-entry persons as
    # past the five-year bar, preserving pre-5-year-bar behavior for
    # households that do not supply this input. Refugee-like or bar-exempt
    # statuses are handled via separate parameter lists rather than this
    # clock.
    reference = "https://www.law.cornell.edu/uscode/text/8/1613"
