def caseconv(case):
    if case == 'l':
        return (lambda s: s.lower())
    else:
        return (lambda s: s.upper())
