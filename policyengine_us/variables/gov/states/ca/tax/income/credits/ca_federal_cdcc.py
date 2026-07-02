from policyengine_us.model_api import *


class ca_federal_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child and Dependent Care Expenses Credit replicated to include California limitations"
    unit = USD
    documentation = "https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # California conforms to the pre-ARPA IRC 21(e)(2) joint-return
        # requirement and its 21(e)(4) separated-taxpayer exception
        # (FTB 3506 instructions, Section E).
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        relevant_expenses = tax_unit("ca_cdcc_relevant_expenses", period)
        credit_rate = tax_unit("ca_cdcc_rate", period)

        return eligible * relevant_expenses * credit_rate
