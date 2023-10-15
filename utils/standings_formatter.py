from texttable import Texttable

def print_standings(header: list[str], standings: list[list[str | int]], dtypes: list[str] = None):
    t = Texttable()
    t.add_rows([header, *standings])
    t.set_header_align(['c']*len(header))
    t.set_cols_align(['c']*len(header))
    # t.set_cols_dtype(dtypes)
    t.set_max_width(0)
    print(t.draw())