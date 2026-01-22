from policyengine_us.model_api import *


class ca_child_care_family_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "California child care family fee"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=10290.&lawCode=WIC"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care
        smi = spm_unit("ca_child_care_smi", period)
        income = spm_unit("ca_child_care_countable_income", period)

        # Families below 75% SMI are exempt from fees
        fee_exemption_threshold = smi * p.family_fees.exemption_threshold
        exempt = income < fee_exemption_threshold

        # Fee capped at 1% of adjusted monthly income for families at/above 75% SMI
        fee_amount = income * p.family_fees.fee_cap

        return where(exempt, 0, fee_amount)
