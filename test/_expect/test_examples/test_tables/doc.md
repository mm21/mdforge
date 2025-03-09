<!-- table start -->

---------- ----------
Cell 1-1   Cell 1-2  

Cell 2-1   Cell 2-2  
---------------------

<!-- table end -->

<!-- table start: align=['left', 'center', 'right'] -->

-------- -------- --------
Cell 1    Cell 2    Cell 3

--------------------------

<!-- table end -->

<!-- table start: block=True -->

+----------+----------+
| Header 1 | Header 2 |
+==========+==========+
| Cell 1   | Cell 2   |
+==========+==========+
| Footer 1 | Footer 2 |
+==========+==========+

<!-- table end -->

<!-- table start: block=True -->

+----------+---------------------+
| Column 1 | Columns 2 & 3       |
|          +----------+----------+
|          | Column 2 | Column 3 |
+==========+==========+==========+
| Cell 1-1 | Cell 1-2 | Cell 1-3 |
+----------+----------+----------+
| Cell 2-1 | Cell 2-2 | Cell 2-3 |
+----------+----------+----------+

<!-- table end -->

<!-- table start: align=['left', 'center', 'right'], block=True, loose=True -->

+:-----------------------------------------------+:-------------:+--------------:+
| This text is implicitly wrapped in a paragraph | <p>Cell 2</p> | <p>Cell 3</p> |
|                                                |               |               |
| - Item 1                                       |               |               |
| - Item 2                                       |               |               |
| <!-- end of list -->                           |               |               |
+------------------------------------------------+---------------+---------------+

<!-- table end -->

<!-- table start: widths=[15, 20] -->

----------------- ----------------------
Short text        This is longer text   
                  that will be wrapped  

----------------------------------------

<!-- table end -->

<!-- table start: widths_pct=[25, 75] -->

----------- -----------------------------
25% width   75% width                    

-----------------------------------------

<!-- table end -->
