import sys
from collections import defaultdict


def args():
    if len(sys.argv) < 3:
        raise Exception("Input must contain <order_file> and <product_file>")
    return sys.argv[1], sys.argv[2]


def split_quoted_line(line):
    """
    This takes care of quoted lines but it is too slow in python
    """
    out = []
    i = 0
    begin_el = 0
    while i < len(line):
        if line[i] == '"':
            i += 1
            # this handles escaped quoted sequences within
            # a quoted environment i.e. it handles \""
            # correctly
            while (i < len(line) and
                   (line[i] != '"' or
                    (line[i] == '"' and
                     (((i-1) >= 0 and line[i-1] == '\\') or
                      ((i-2) >= 0 and line[i-1] == '"' and
                       line[i-2] == '\\'))))):
                i += 1
            if i < len(line):
                # Add extra for the closing quote
                i += 1
            continue
        elif line[i] == ",":
            out.append(line[begin_el:i])
            i += 1
            begin_el = i
        else:
            i += 1
    if begin_el < i:
        out.append(line[begin_el:i])
    return out


def read_table(afile, fields):
    """
    generator for generic csv file
    inputs
    afile: filename
    fields: which fields to extract
    """
    first_line = True
    try:
        with open(afile, 'r') as f:
            for line in f:
                line = line.strip()
                if first_line is True:
                    top_fields = line.split(",")
                    fidx = []
                    for i, f in enumerate(top_fields):
                        if f in fields:
                            fidx.append(i)
                    first_line = False
                    continue
                el = split_quoted_line(line)
                if el[0][0] == "#":
                    continue
                if len(el) != len(top_fields):
                    continue
                yield [x for i, x in enumerate(el) if i in fidx]
    except Exception as e:
        print(e)
        return


def read_prod_table(product_file):
    """
    generator for product file
    yields the product id and the corresponding department id
    """
    first_line = True
    try:
        with open(product_file, 'r') as f:
            for line in f:
                if first_line is True:
                    first_line = False
                    continue
                line = line.strip()

                # ignore lines that do not start with a number
                # e.g. to insert lines with comments
                if line[0:line.find(",")].isdigit():
                    # separate first column from the rest
                    prod_id, rest = line.strip().split(",", 1)

                    # Get rid of product names with special characters
                    if rest[0] == '"':
                        endp = rest.rfind('"', 1)
                        rest = "_" + rest[(endp+1):]

                    _, _, dept_id = rest.split(",")
                else:
                    continue
                yield prod_id, dept_id
    except Exception as e:
        print(e)
        return


def read_order_table(order_file):
    """
    generator for order file
    yields the product id and the reorder flag
    """

    try:
        with open(order_file, 'r') as f:
            first_line = True

            for line in f:
                if first_line:
                    first_line = False
                    continue
                line = line.strip()

                # skip lines that don't start with a number
                # example comment lines
                if line[0:line.find(",")].isdigit():
                    _, prod, _, reorder = line.split(',')
                else:
                    continue
                yield prod, reorder

    except ValueError as e:
        print(e, line)
        return
    except Exception as e:
        print(e)
        return


def main():

    # Get arguments
    order_file, product_file = args()

    # Iterators for the files
    hard_code_line_parser = True
    if hard_code_line_parser:
        prod_gen = read_prod_table(product_file)
        order_gen = read_order_table(order_file)
    else:
        prod_gen = read_table(product_file, ['product_id', 'department_id'])
        order_gen = read_table(order_file, ['product_id', 'reordered'])

    # Populate product_hash (iterate through product table)
    prod_h = {}
    depts = set()
    for p in prod_gen:
        prod, dept = p
        prod_h[prod] = dept
        depts.add(dept)

    # Initialize results
    agg = defaultdict(dict)
    for d in depts:
        agg[d]['orders'] = 0
        agg[d]['first'] = 0

    # Iterate through order table
    for o in order_gen:
        order, reorder = o
        # ignore order if there is no corresponding department
        if order in prod_h:
            agg[prod_h[order]]['orders'] += 1
            agg[prod_h[order]]['first'] += (reorder == "0") * 1

    # Print results
    print("department_id,number_of_orders,number_of_first_orders,percentage")
    for _, k in sorted([(int(x), x) for x in agg.keys()
                        if agg[x]['orders'] > 0]):
        order, first = agg[k]['orders'], agg[k]['first']
        print(",".join([k,
                        str(order),
                        str(first),
                        "{:0.2f}".format(round(first/order, 2))]))


if __name__ == '__main__':
    main()
