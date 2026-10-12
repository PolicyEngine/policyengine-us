from policyengine_us.model_api import *


class ma_ccfa_uncapped_daily_payment(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts Child Care Financial Assistance (CCFA) uncapped daily payment per child"
    unit = USD
    reference = "https://www.mass.gov/doc/eecfy26-rate-increase-chart/download#page=1"
    definition_period = MONTH
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        center_based_payment = person("ma_ccfa_center_based_reimbursement", period)
        head_start_partner_and_kindergarten_payment = person(
            "ma_ccfa_head_start_partner_and_kindergarten_reimbursement", period
        )
        informal_child_care_payment = person(
            "ma_ccfa_informal_child_care_reimbursement", period
        )
        family_child_care_payment = person(
            "ma_ccfa_family_child_care_reimbursement", period
        )

        care_provider_type = person("ma_ccfa_care_provider_type", period)
        care_provider_types = care_provider_type.possible_values
        return select(
            [
                care_provider_type == care_provider_types.CENTER_BASED_CARE,
                care_provider_type
                == care_provider_types.HEAD_START_PARTNER_AND_KINDERGARTEN,
                care_provider_type == care_provider_types.INFORMAL_CHILD_CARE,
                care_provider_type == care_provider_types.FAMILY_CHILD_CARE,
            ],
            [
                center_based_payment,
                head_start_partner_and_kindergarten_payment,
                informal_child_care_payment,
                family_child_care_payment,
            ],
            default=0,
        )
