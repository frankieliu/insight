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
   `product_id` and `department_id` since we want to count the
   number of orders and first time orders by department.

## Output

Output is a single file called `report.csv` in the `output` directory
with `number_of_orders`, `number_of_first_orders` and a `percentage`.

***Nb. instructions call it `percentage`, but really it is a ratio.***

Output should be sorted by `department_id`, if there are no orders
from a department, should not list it.  `percentage` is rounded to
the second decimal place (i.e. hundredths).

## Running instructions

`run.sh` is a bash script.  It requires an executable `python3` to be
in the path, there are no other dependencies.  Main program is found
in `src` directory.

## Approach

1. There is a generic args() function for taking the input file names
   from the CLI.
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
1. In general, I tried not importing any external modules, to lower
   the dependencies for running this code.
1. For a more robust CLI parser, `getopt` could be used.
1. For parsing the two csv files, one should just use `csv.reader`, with the
   `quotechar='"'` `quoting=csv.QUOTE_ALL`, and
   `skipinitialspace=True` option, these should take care of any
    commas within the quotes.
1. For extensibility, a schema should be passed to the generators or
   the first line of the file could be used to derive name and number of fields,
   and a list of fields could be passed to the generator, so that only required
   fields are returned.
   1. Code was refactored to allow for deriving the schema from the
      first line.  set `hard_code_line_parser = False` to derive
      schema from the first line.  This basically removes the
      duplication of code in `read_prod_table` and `read_order_table`,
      into a generic `read_table` which specifies which fiels to
      return back.  Proper handling of quoted strings is also handled
      by the generator, making use of `split_quoted_line`
   1. I kept the old hard-wired code because of speed when doing it on a
      large file.

## Complexity
1. Time complexity: O(# product ids + # orders)
1. Space complexity: O(# product ids + # departments)
1. The time complexity is due to the hash
   map creation plus the time to go through the orders.  The space
   complexity is for storing the hash map and the aggregate count for
   each department.

## Scalability issues
1. For much a larger product to department relational table, say with
   1 billion elements, it would become prohibitively large to store in
   memory.  In this case, we could create a smaller hash map with 10
   million elements, such that only a subset of the products are
   represented.

1. We can then pipe the order list line by line through this first
   hash map and aggregate on the products that have an entry on the
   hash map.  If the product id is found in the hash map, then it need
   not go to the next stage in the pipeline.  Only elements which are
   not found in the hash map are passed on to next stage.

1. Each stage contains another subset of the "larger" hash map, e.g.
   another 10 million entries

1. After all lines go through the system, the individual processing
   units forward their aggregates to a central processing unit to
   reduce the count from each of the pipeline stages.

1. Each order line, may in the worst case, may pass through all the
   processing blocks.  The time complexity still has O(# of orders).
   In particular, it is not multiplied by O(# products), which is
   proportional to the number of processing stages, because lines
   arrive in a pipeline fashion, i.e. nothing is waiting for the next
   item to be processed.  However latency is increased, but we can
   argue that for long enough order lists, this latency is
   insignificant.

1. At each stage interface, one can add a message queue, so as to
   allow for asynchronous pipelining, similarly the reduce block can
   communicate with the other HM blocks via a message queue, so that
   the internal state in the reducer does not have to handle the
   concurrent requests coming from the pipeline stages.  For this
   topology, the individual pipeline stages can locally aggregate
   until an "EOF" or "stop" signal goes through it, at which point it
   sends its results to the reducer.

   <img src="pipeline.png" width="900">

## Test cases
1. Added `test_2` to make sure that departments with zero order are not
   reported.
1. Added `test_2` # comment rows in orders, so as to exclude certain
   order rows from the input.
1. Added `test_3` to check functionality of orders which have no matching
   department, they are dropped from the count.
1. Added `test_3` # comment rows in products, so as to exclude prod-dept rows
   from the input.
1. Added `test_4` to check handling of commas within quoted string.

## Extensions
