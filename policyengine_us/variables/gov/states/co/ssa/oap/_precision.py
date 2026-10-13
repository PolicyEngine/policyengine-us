# Monthly amounts derived from annual float32 inputs carry residue of about
# $0.0001 near $1,000. The rule's own arithmetic produces half cents (earnings
# are halved), so a tenth of a cent separates residue from a real difference.
PRECISION = 0.001
