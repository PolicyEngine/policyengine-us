from policyengine_us.model_api import *


class il_hbwd_countable_assets(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities countable assets"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.381",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # HBWD exempt assets include:
        # - Primary residence
        # - One vehicle
        # - Retirement accounts inaccessible before age 59.5
        # - Medical savings accounts
        # For now, return total SPM unit assets as we don't have detailed asset breakdowns
        # TODO: Implement specific asset exemptions when asset variables are available
        # Use period.this_year since assets are stocks, not flows
        return person.spm_unit("spm_unit_assets", period.this_year)
