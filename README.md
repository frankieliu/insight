# Insight Coding Challenge

Insight coding challenge

## Problem

SELECT * GROUPBY department COUNT number of requests COUNT number of first time
requests CREATE ratio: number of first time requests/number of requests

## Submission

* Added `insight-cc-bot` into list of collaborators
* [Invite link](https://github.com/frankieliu/insight/invitations)

## Input

Two files from the `input` directory:

1. `order_products.csv` with columns `order_id`, `product_id`,
    `add_to_cart_order`, `reordered`, which are respectively, id for
    the order, id for the product, sequence order added to cart, and
    flag indicating if the product has been used by this user at some
    point in the past, `1` if ordered in the past and `0` if first
    time.

1. `products.csv` with `product_id`, `product_name`, `aisle_id`,
   `department_id`, all we care about is the relationship between
   `product_id` and and `department_id` since we want to count the
   number of orders and first time orders by department.

## Output

Output is a single file called `report.csv` in the `output` directory
with `number_of_orders`, `number_of_first_orders` and a `percentage`.

***Nb. instructions call it `percentage`, but really it is a ratio.***

Output should be sorted by `department_id`, if there are no orders for
a department should not list it.  `percentage` is rouded to second
decimal.

## Running instructions

`run.sh` is bash script.  Requires executable `python3` to be in the path, there
are no other dependencies.  Main program is found in `src` directory.

## Approach

1. There is a generic args() function for taking the input file name from the CLI.
1. There are two generators for parsing through the input files.
1. There is a main which does the following:
   1. Generate a hash map from `product_id` to `department_id`
   1. For each department create a dataframe containing `orders` and
      `first` "columns".  It would be more natural to use pandas here
      for a column, but for this exercise just using a dictionary for
      each department, think of them as attributes or fields for each
      department.
   1. Go through each line in the order file, and increment the respective
      counters.
   1. Filter the result by departments that have an order and output a
      ratio of the first time orders to number of orders.

## General considerations

1. A more robust CLI parser getopt should be used.
1. For parsing csv files it is best to just use `csv.reader`, with the `quotechar='"'`
   `quoting=csv.QUOTE_ALL`, and `skipinitialspace=True` option, since these should
   take of the comma's within the quotes.
1. Time complexity: O(# product ids + # orders), Space complexity: O(#
   product ids + # departments) The time complexity is due to the hash
   map creation plus the time to go through the orders.  The space
   complexity is for storing the hash map and the aggregate count for
   each department.

## Scalability issues
1. Here we can deal with a relatively large hash map for products to
department.  But for larger

## Test cases

## Extensions
