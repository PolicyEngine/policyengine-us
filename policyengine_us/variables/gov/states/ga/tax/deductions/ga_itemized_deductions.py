from policyengine_us.model_api import *


class ga_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500",
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=14c633e3-6517-481d-90d5-8e8340415643&pdistocdocslideraccess=true&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcomponentid=234187&pdtocnodeidentifier=ABWAALAADAAN&ecomp=k2vckkk&prid=a2b8e5c1-a075-4bcb-8484-2a0337552eb2",
    )
    defined_for = StateCode.GA

    # GA itemized deduction does not account for mortgage expenses
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        is_itemized = tax_unit("tax_unit_itemizes", period) # whether if taxunit itemized deductions on Federal return
        federal_itemized_deductions = tax_unit("itemized_deductions_less_salt", period)


        ##- charitable_deduction
        ##- interest_deduction
        ##- salt_deduction
        ##- medical_expense_deduction
        ##- casualty_loss_deduction
        ##- qualified_business_income_deduction
        
        ## adjustment -minus
        # income taxes other than georgia
        # investment interest expense for the productions of income exempt

        interest_deduction = tax_unit("interest_deduction",period)

        income_adjustment = federal_taxable_income - ga_taxable_income ##????

        ga_itemized_deductions = itemized_deductions - interest_deduction
        


        return add(tax_unit, period, itm_deds)
