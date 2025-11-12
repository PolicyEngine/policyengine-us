from policyengine_us.model_api import *


class tx_fpp_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Family Planning Program income limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.healthytexaswomen.org/healthcare-programs/family-planning-program/fpp-who-can-apply",
        "https://www.hhs.texas.gov/sites/default/files/documents/texas-womens-health-programs-report-2024.pdf",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Get the Federal Poverty Guideline for this SPM unit
        fpg = spm_unit("spm_unit_fpg", period)

        # Get FPG percentage (250% = 2.5)
        p = parameters(period).gov.states.tx.fpp

        # Return annual income limit (FPG * percentage)
        return fpg * p.fpg_percentage
