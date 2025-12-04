from policyengine_us.model_api import *


class il_smib(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Illinois SMIB Buy-In Program benefit"
    definition_period = MONTH
    documentation = (
        "Illinois Supplementary Medical Insurance Benefit (SMIB) Buy-In "
        "Program. The state pays Medicare Part B premiums for eligible "
        "individuals receiving AABD, TANF, SSI, or who qualify under the "
        "Medicare Savings Program (QMB, SLMB, QI)."
    )
    reference = (
        "https://www.ilga.gov/commission/jcar/admincode/089/089001200D00700R.html",
        "https://www.dhs.state.il.us/page.aspx?item=18685",
    )
    defined_for = StateCode.IL
    adds = ["il_smib_person"]
