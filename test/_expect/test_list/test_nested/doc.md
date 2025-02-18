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
  1. d1
  1. d2
  1. d3
     <!-- start: NumberedList(loose=False) -->
     1. d3-1
     1. d3-2
     1. d3-3
     <!-- end: NumberedList(loose=False) -->
  <!-- end: NumberedList(loose=False) -->
<!-- end: BulletList(loose=False) -->

# NumberedList

<!-- start: NumberedList(loose=False) -->
1. a
1. b
   <!-- start: NumberedList(loose=False) -->
   1. b1
   1. b2
   1. b3
   <!-- end: NumberedList(loose=False) -->
1. c
   <!-- start: NumberedList(loose=False) -->
   1. c1
   1. c2
   1. c3
      <!-- start: NumberedList(loose=False) -->
      1. c3-1
      1. c3-2
      1. c3-3
      <!-- end: NumberedList(loose=False) -->
   <!-- end: NumberedList(loose=False) -->
1. d (BulletList)
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
