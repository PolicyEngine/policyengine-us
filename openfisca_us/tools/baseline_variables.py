from policyengine_us.system import CountryTaxBenefitSystem

baseline_variables = {
    name: type(variable)
    for name, variable in CountryTaxBenefitSystem().variables.items()
}
