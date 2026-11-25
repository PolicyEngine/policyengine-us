from policyengine_us.model_api import *


class railroad_benefits(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement Board benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Gross annual benefits paid by the Railroad Retirement Board, such as "
        "retirement, disability, spouse and survivor annuities, before Medicare "
        "premiums or other amounts are withheld. Railroad Unemployment Insurance "
        "Act benefits are reported elsewhere: unemployment benefits in "
        "unemployment_compensation and sickness benefits in disability_benefits. "
        "Census counts railroad retirement as a government transfer, and "
        "household and SPM benefits include these benefits. Enter them only "
        "here, not also as social_security, pension_income, disability_benefits "
        "or survivor_benefits."
    )
    default_value = 0
    reference = "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=4"
