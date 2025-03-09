<!-- table start: block=True -->

+--------------------------+----------+
| Test cspan               | Test 0-2 |
+-------------+------------+----------+
| Test rspan  | Test 1-1   | Test 1-2 |
| Test abc    | abc        |          |
| Test def    +------------+----------+
| Test ghi    | Test 2-1   | Test 2-2 |
| Test jkl    |            |          |
+-------------+------------+----------+
| Test cspan and rspan abc | Test 3-2 |
| 0123456789abcdef         +----------+
|                          | Test 4-2 |
+--------------------------+ and      |
| Test 5-0 and Test 5-1    | Test 5-2 |
| abc                      |          |
+-------------+------------+----------+
| Test 6-0    | Test 6-1   | Test 6-2 |
+-------------+------------+----------+

<!-- table end -->

<!-- table start: align=center, block=True -->

+:--------:+:--------:+
| Test 0-0 | Test 0-1 |
| abc      | abc      |
|          +----------+
|          | Test 1-1 |
+----------+----------+
| Test 2-0 | Test 2-1 |
+----------+----------+

<!-- table end -->
