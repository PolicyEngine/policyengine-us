from policyengine_us.model_api import *


class medicaid_ltss_home_ownership_share(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS home ownership share"
    unit = "/1"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit fractional share of the home's equity owned by the LTSS "
        "applicant, from zero to one. For Delaware, supply both spouses' "
        "individual shares in the same retained home on their respective "
        "Person records in one marital unit, with the same whole-home value "
        "and encumbrances. The equity screen sums their shares because DSSM "
        "20320.7.C treats spouses as one owner, regardless of their income "
        "or resource budgeting unit. Do not repeat a combined couple share "
        "on both spouses. Third-party ownership is excluded from that sum. "
        "Zero is the default for an individual with no ownership interest. "
        "The model does not determine title, individual shares, or legal "
        "ownership."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#f",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=17",
    )
