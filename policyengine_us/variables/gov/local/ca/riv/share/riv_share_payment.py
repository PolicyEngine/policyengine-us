from policyengine_us.model_api import *


class riv_share_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Riverside County Sharing Households Assist Riverside's Energy program (SHARE) payment"
    unit = USD
    definition_period = MONTH
    defined_for = "riv_share_eligible"
    reference = "https://riversideca.gov/utilities/residents/assistance-programs/share-english"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.share.payment
        electric_expense = spm_unit("pre_subsidy_electricity_expense", period)
        electric_payment = min_(electric_expense, p.electric)
        electric_emergency_payment = spm_unit(
            "riv_share_electric_emergency_payment", period
        )

        water_expense = spm_unit("water_expense", period)
        water_payment = min_(water_expense, p.water)

        trash_expense = spm_unit("trash_expense", period)
        trash_payment = min_(trash_expense, p.trash)

        return (
            electric_payment
            + electric_emergency_payment
            + water_payment
            + trash_payment
        )
