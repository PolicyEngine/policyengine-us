from policyengine_us.model_api import *


class armed_forces_retirement_pay_survivors(Variable):
    value_type = float
    entity = Person
    label = "Armed forces retirement survivor benefit payments"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Military retirement survivor benefit payments from service in the "
        "armed forces, excluding survivor annuities from the NOAA and Public "
        "Health Service commissioned corps."
    )
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title10-section101",
    )

    def formula(person, period, parameters):
        armed_forces = person("military_retirement_pay_is_armed_forces", period)
        return person("military_retirement_pay_survivors", period) * armed_forces
