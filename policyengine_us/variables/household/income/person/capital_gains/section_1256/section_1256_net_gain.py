from policyengine_us.model_api import *


class section_1256_net_gain(Variable):
    value_type = float
    entity = Person
    label = "Net gain or loss on section 1256 contracts"
    documentation = (
        "Net gain (negative for loss) on regulated futures, foreign currency "
        "contracts, nonequity options, dealer equity options and dealer "
        "securities futures, including the year-end mark-to-market of open "
        "positions (Form 6781 Part I line 7, after any loss carryback "
        "election). Do not also report it in short- or long-term gains."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1256",
        "https://www.irs.gov/forms-pubs/about-form-6781",
    )
