from policyengine_us.model_api import *


class ny_liheap_cooling_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "NY HEAP cooling assistance benefit"
    definition_period = YEAR
    defined_for = "ny_liheap_income_eligible"
    unit = USD
    reference = "https://otda.ny.gov/programs/heap/"
    documentation = """NY HEAP Cooling Assistance program provides air conditioners 
    or fans to eligible households. This is an equipment program, not a cash benefit.
    The value represents the equipment cost, typically $800 for AC units or $60 for fans."""

    def formula(spm_unit, period, parameters):
        # NY HEAP Cooling Assistance provides equipment (AC units or fans), not cash
        # The benefit is available May through August for households with:
        # - Documented medical need, or
        # - Member who is elderly, disabled, or child under 6
        #
        # Equipment provided:
        # - Air conditioner (up to $800) once every 10 years
        # - Fan ($60) if AC not feasible
        #
        # Since PolicyEngine models cash benefits and this is equipment provision,
        # we return 0. A full implementation would need to track:
        # - Medical documentation requirements
        # - 10-year replacement cycle for AC units
        # - Installation costs (additional benefit)
        return 0
