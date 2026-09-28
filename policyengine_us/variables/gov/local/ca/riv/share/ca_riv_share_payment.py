from policyengine_us.model_api import *


class ca_riv_share_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Riverside County Sharing Households Assist Riverside's Energy program (SHARE) payment"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Riverside Public Utilities' SHARE program credits electric, water, and "
        "trash bills for income-qualified customers. The utility serves the "
        "City of Riverside rather than the whole county, but the model has no "
        "utility-territory input, so it applies SHARE to every eligible "
        "Riverside County household."
    )
    defined_for = "ca_riv_share_eligible"
    reference = (
        "https://riversideca.gov/utilities/residents/assistance-programs/share-english"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.cap.share.payment
        electricity_expense = spm_unit("pre_subsidy_electricity_expense", period)
        capped_electricity_payment = min_(electricity_expense, p.electricity)
        electricity_emergency_payment = spm_unit(
            "ca_riv_share_electricity_emergency_payment", period
        )

        water_expense = spm_unit("water_expense", period)
        capped_water_payment = min_(water_expense, p.water)

        trash_expense = spm_unit("trash_expense", period)
        capped_trash_payment = min_(trash_expense, p.trash)

        return (
            capped_electricity_payment
            + electricity_emergency_payment
            + capped_water_payment
            + capped_trash_payment
        )
