from policyengine_us.model_api import *


class medicaid_ltss_reported_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Reported Medicaid LTSS gross monthly earned income"
    unit = USD
    definition_period = MONTH
    default_value = -1
    documentation = (
        "Each person's actual monthly work income before Medicaid LTSS "
        "income exclusions or qualified income trust deposits. A "
        "nonnegative amount, including zero, replaces the equal monthly "
        "allocation of existing annual gross SSI earned-income sources. "
        "The default -1 means unspecified and preserves that annual-source "
        "default for this person, including when other people report "
        "actual monthly amounts. Include work income outside those "
        "existing sources when reporting the actual month's amount. Each "
        "spouse reports their own income; the model combines it when "
        "couple budgeting applies."
    )
    reference = "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=5"
