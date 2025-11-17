from policyengine_us.model_api import *


class il_hbwd_premium(Variable):
    value_type = float
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities monthly premium"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://hfs.illinois.gov/medicalprograms/hbwd/premiums.html",
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
    )
    defined_for = "il_hbwd_eligible"

    # TODO: Implement 2D lookup table from HBWD premium schedule
    # Premium is based on both earned and unearned income brackets
    # See hfsweb004.pdf for complete premium table
    # Maximum premium is $500/month
