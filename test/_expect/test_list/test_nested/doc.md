# BulletList

<!-- start: BulletList(loose=False) -->
- a
- b
  <!-- start: BulletList(loose=False) -->
  - b1
  - b2
  - b3
  <!-- end: BulletList(loose=False) -->
- c
  <!-- start: BulletList(loose=False) -->
  - c1
  - c2
  - c3
    <!-- start: BulletList(loose=False) -->
    - c3-1
    - c3-2
    - c3-3
    <!-- end: BulletList(loose=False) -->
  <!-- end: BulletList(loose=False) -->
- d (NumberedList)
  <!-- start: NumberedList(loose=False) -->
  #. d1
  #. d2
  #. d3
     <!-- start: NumberedList(loose=False) -->
     #. d3-1
     #. d3-2
     #. d3-3
     <!-- end: NumberedList(loose=False) -->
  <!-- end: NumberedList(loose=False) -->
<!-- end: BulletList(loose=False) -->

# NumberedList

<!-- start: NumberedList(loose=False) -->
#. a
#. b
   <!-- start: NumberedList(loose=False) -->
   #. b1
   #. b2
   #. b3
   <!-- end: NumberedList(loose=False) -->
#. c
   <!-- start: NumberedList(loose=False) -->
   #. c1
   #. c2
   #. c3
      <!-- start: NumberedList(loose=False) -->
      #. c3-1
      #. c3-2
      #. c3-3
      <!-- end: NumberedList(loose=False) -->
   <!-- end: NumberedList(loose=False) -->
#. d (BulletList)
   <!-- start: BulletList(loose=False) -->
   - d1
   - d2
   - d3
     <!-- start: BulletList(loose=False) -->
     - d3-1
     - d3-2
     - d3-3
     <!-- end: BulletList(loose=False) -->
   <!-- end: BulletList(loose=False) -->
<!-- end: NumberedList(loose=False) -->
