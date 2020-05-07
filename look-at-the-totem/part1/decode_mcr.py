#!/usr/bin/env python3

OPS = {
    'add': 0xfe021410,
    'delete': 0xfe000438,
    'edit': 0xfe021478,
    'get': 0xfe021458,
    'search': 0xfe012492,
}


def parse_mcr2(encoded):
    val = encoded & 0xffffffff
    assert (val >> 24) == 0xfe

    assert val & ((1 << 20) | (1 << 4)) == (1 << 4)

    return {
        'opc1': (val >> 21) & 0x7,
        'CRn': (val >> 16) & 0xf,
        'Rt': (val >> 12) & 0xf,
        'coproc': (val >> 8) & 0xf,
        'opc2': (val >> 5) & 0x7,
        'CRm': val & 0xf
    }


if __name__ == '__main__':
    for opname, opc in OPS.items():
        print('{opname:6}: {parsed}'.format(opname=opname,
                                            parsed=parse_mcr2(opc)))
