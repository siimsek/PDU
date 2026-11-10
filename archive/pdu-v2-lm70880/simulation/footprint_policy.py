"""User-approved prototype assignments; F1 remains deliberately unselected.

These are identity checks, not manufacturing qualification. LM70880's
rectangular land approximation still requires stencil/thermal review.
"""
EXPECTED_FOOTPRINTS = {
    'U1': 'PDU:LM70880_RRX0029B_RectLands',
    'U2': 'PDU:LM70880_RRX0029B_RectLands',
    'U3': 'PDU:TPS25982_RGE0024M',
    'U4': 'PDU:TPS25982_RGE0024M',
    'F1': '',
}
EXPECTED_FOOTPRINTS.update({f'COUT{i}':'PDU:TDK_C5750_2220_Recommended'
                            for i in range(1,9)})


def matches(comps):
    return all(comps[ref]['footprint'] == fp
               for ref, fp in EXPECTED_FOOTPRINTS.items())
