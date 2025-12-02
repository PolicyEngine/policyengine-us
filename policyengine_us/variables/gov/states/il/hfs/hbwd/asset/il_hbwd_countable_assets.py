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
        # HBWD exempt assets per § 120.381:
        # - Primary residence (homestead)
        # - Personal effects and household goods
        # - One vehicle (full exemption if essential, $4,500 if not)
        # - Life insurance ≤$1,500
        # - Burial resources
        # - Retirement accounts inaccessible before age 59.5
        # - Medical savings accounts (26 USC 220)
        # Currently only implementing vehicle exemption
        # § 120.381 and § 113.141 have identical vehicle exemption rules,
        # so using AABD vehicle calculation
        cash_assets = person.spm_unit("spm_unit_cash_assets", period.this_year)
        vehicle_value = person.spm_unit(
            "il_aabd_countable_vehicle_value", period
        )
        # TODO: Implement homestead, retirement account, burial, and other exemptions
        return cash_assets + vehicle_value
