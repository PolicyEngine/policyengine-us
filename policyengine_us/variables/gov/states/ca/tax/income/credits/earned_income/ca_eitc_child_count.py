from policyengine_us.model_api import *


class ca_eitc_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "CalEITC qualifying children"
    definition_period = YEAR
    documentation = """
    Number of qualifying children who meet the CalEITC identification
    requirement (ca_is_qualifying_child_for_caleitc). Beginning in 2020,
    California accepts an ITIN or SSN rather than requiring a work-valid
    SSN; earlier years match the federal EITC child count.
    """
    reference = (
        # AB 1876, section 1, R&TC 17052(p): ITIN or SSN from 2020.
        "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201920200AB1876",
        # FTB 3514, Step 1 question 3 and Line 7: qualifying children's IDs.
        "https://www.ftb.ca.gov/forms/2020/2020-3514-instructions.html",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["ca_is_qualifying_child_for_caleitc"])
