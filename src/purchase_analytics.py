import sys
from collections import defaultdict


def args():
    if len(sys.argv) < 3:
        raise Exception("Input must contain <order_file> and <product_file>")
    return sys.argv[1], sys.argv[2]


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

                # separate first column from the rest
                prod_id, rest = line.strip().split(",", 1)

                # Get rid of product names with special characters
                if rest[0] == '"':
                    endp = rest.rfind('"', 1)
                    rest = "_" + rest[(endp+1):]

                _, _, dept_id = rest.split(",")
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
                _, prod, _, reorder = line.strip().split(',')
                yield prod, reorder == "0"
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
    prod_gen = read_prod_table(product_file)
    order_gen = read_order_table(order_file)

    # Populate product_hash
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

    for o in order_gen:
        order, reorder = o
        agg[prod_h[order]]['orders'] += 1
        agg[prod_h[order]]['first'] += reorder * 1

    # print results
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
