from policyengine_us.model_api import *


class il_smib_categorical_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois SMIB categorical eligibility"
    definition_period = MONTH
    documentation = (
        "Eligible for SMIB based on categorical eligibility: "
        "receiving AABD, TANF, or SSI benefits."
    )
    reference = (
        "https://www.ilga.gov/commission/jcar/admincode/089/089001200D00700R.html",
        "https://www.dhs.state.il.us/page.aspx?item=18685",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # AABD recipient
        is_aabd = person("il_aabd_eligible_person", period)
        # TANF recipient (SPM unit level, check if person is in eligible unit)
        is_tanf = person.spm_unit("il_tanf_eligible", period)
        # SSI recipient
        is_ssi = person("is_ssi_eligible", period)
        return is_aabd | is_tanf | is_ssi
