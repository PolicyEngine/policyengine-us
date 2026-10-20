from policyengine_us.model_api import *


class ca_eitc_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "CalEITC qualifying children"
    definition_period = YEAR
    documentation = """
    Number of otherwise qualifying children who meet the CalEITC
    identification requirement. Beginning in 2020, California accepts an
    ITIN or SSN rather than requiring a work-valid SSN. Earlier years use
    the federal EITC child count.
    """
    reference = (
        # AB 1876, section 1, R&TC 17052(p): ITIN or SSN from 2020.
        "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201920200AB1876",
        # FTB 3514, Step 1 question 3 and Line 7: qualifying children's IDs.
        "https://www.ftb.ca.gov/forms/2020/2020-3514-instructions.html",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("eitc_child_count", period)

    def formula_2020(tax_unit, period, parameters):
        person = tax_unit.members
        is_child = person("is_eitc_qualifying_child", period)
        has_tin = person("has_tin", period)
        return tax_unit.sum(is_child & has_tin)
