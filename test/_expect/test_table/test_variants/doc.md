# Inline tables

## No header or footer, 1 rows

<!-- table start: align=['left', 'center', 'right', 'default'] -->

------ ------ ------ ------
Cell    Cell    Cell Cell  
0-0     0-1      0-2 0-3   

---------------------------

<!-- table end -->

## With header, 1 rows

<!-- table start: align=['left', 'center', 'right', 'default'] -->

-------------------------------------------------------------
Header 0,        Header 1,         Header 2, Header 3,       
align: left    align: center    align: right align: default  
------------- --------------- -------------- ----------------
Cell               Cell                 Cell Cell            
0-0                 0-1                  0-2 0-3             

-------------------------------------------------------------

<!-- table end -->

## No header or footer, 3 rows

<!-- table start: align=['left', 'center', 'right', 'default'] -->

------ ------ ------ ------
Cell    Cell    Cell Cell  
0-0     0-1      0-2 0-3   

Cell    Cell    Cell Cell  
1-0     1-1      1-2 1-3   

Cell    Cell    Cell Cell  
2-0     2-1      2-2 2-3   
---------------------------

<!-- table end -->

## With header, 3 rows

<!-- table start: align=['left', 'center', 'right', 'default'] -->

-------------------------------------------------------------
Header 0,        Header 1,         Header 2, Header 3,       
align: left    align: center    align: right align: default  
------------- --------------- -------------- ----------------
Cell               Cell                 Cell Cell            
0-0                 0-1                  0-2 0-3             

Cell               Cell                 Cell Cell            
1-0                 1-1                  1-2 1-3             

Cell               Cell                 Cell Cell            
2-0                 2-1                  2-2 2-3             
-------------------------------------------------------------

<!-- table end -->

# Block tables

## No header or footer, 1 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+:-----+:----:+-----:+------+
| Cell | Cell | Cell | Cell |
| 0-0  | 0-1  | 0-2  | 0-3  |
+------+------+------+------+

<!-- table end -->

## With header, 1 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+-------------+---------------+--------------+----------------+
| Header 0,   | Header 1,     | Header 2,    | Header 3,      |
| align: left | align: center | align: right | align: default |
+:============+:=============:+=============:+================+
| Cell        | Cell          | Cell         | Cell           |
| 0-0         | 0-1           | 0-2          | 0-3            |
+-------------+---------------+--------------+----------------+

<!-- table end -->

## With footer, 1 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+:-------+:------:+-------:+--------+
| Cell   | Cell   | Cell   | Cell   |
| 0-0    | 0-1    | 0-2    | 0-3    |
+========+========+========+========+
| Footer | Footer | Footer | Footer |
| 0      | 1      | 2      | 3      |
+========+========+========+========+

<!-- table end -->

## With header and footer, 1 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+-------------+---------------+--------------+----------------+
| Header 0,   | Header 1,     | Header 2,    | Header 3,      |
| align: left | align: center | align: right | align: default |
+:============+:=============:+=============:+================+
| Cell        | Cell          | Cell         | Cell           |
| 0-0         | 0-1           | 0-2          | 0-3            |
+=============+===============+==============+================+
| Footer      | Footer        | Footer       | Footer         |
| 0           | 1             | 2            | 3              |
+=============+===============+==============+================+

<!-- table end -->

## No header or footer, 3 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+:-----+:----:+-----:+------+
| Cell | Cell | Cell | Cell |
| 0-0  | 0-1  | 0-2  | 0-3  |
+------+------+------+------+
| Cell | Cell | Cell | Cell |
| 1-0  | 1-1  | 1-2  | 1-3  |
+------+------+------+------+
| Cell | Cell | Cell | Cell |
| 2-0  | 2-1  | 2-2  | 2-3  |
+------+------+------+------+

<!-- table end -->

## With header, 3 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+-------------+---------------+--------------+----------------+
| Header 0,   | Header 1,     | Header 2,    | Header 3,      |
| align: left | align: center | align: right | align: default |
+:============+:=============:+=============:+================+
| Cell        | Cell          | Cell         | Cell           |
| 0-0         | 0-1           | 0-2          | 0-3            |
+-------------+---------------+--------------+----------------+
| Cell        | Cell          | Cell         | Cell           |
| 1-0         | 1-1           | 1-2          | 1-3            |
+-------------+---------------+--------------+----------------+
| Cell        | Cell          | Cell         | Cell           |
| 2-0         | 2-1           | 2-2          | 2-3            |
+-------------+---------------+--------------+----------------+

<!-- table end -->

## With footer, 3 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+:-------+:------:+-------:+--------+
| Cell   | Cell   | Cell   | Cell   |
| 0-0    | 0-1    | 0-2    | 0-3    |
+--------+--------+--------+--------+
| Cell   | Cell   | Cell   | Cell   |
| 1-0    | 1-1    | 1-2    | 1-3    |
+--------+--------+--------+--------+
| Cell   | Cell   | Cell   | Cell   |
| 2-0    | 2-1    | 2-2    | 2-3    |
+========+========+========+========+
| Footer | Footer | Footer | Footer |
| 0      | 1      | 2      | 3      |
+========+========+========+========+

<!-- table end -->

## With header and footer, 3 rows

<!-- table start: align=['left', 'center', 'right', 'default'], block=True -->

+-------------+---------------+--------------+----------------+
| Header 0,   | Header 1,     | Header 2,    | Header 3,      |
| align: left | align: center | align: right | align: default |
+:============+:=============:+=============:+================+
| Cell        | Cell          | Cell         | Cell           |
| 0-0         | 0-1           | 0-2          | 0-3            |
+-------------+---------------+--------------+----------------+
| Cell        | Cell          | Cell         | Cell           |
| 1-0         | 1-1           | 1-2          | 1-3            |
+-------------+---------------+--------------+----------------+
| Cell        | Cell          | Cell         | Cell           |
| 2-0         | 2-1           | 2-2          | 2-3            |
+=============+===============+==============+================+
| Footer      | Footer        | Footer       | Footer         |
| 0           | 1             | 2            | 3              |
+=============+===============+==============+================+

<!-- table end -->
