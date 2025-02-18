# BulletList, 1 element

<!-- start: BulletList(loose=True) -->
- <p>a</p>

<!-- end: BulletList(loose=True) -->

# BulletList, implicit loose (paragraphs)

<!-- start: BulletList(loose=True) -->
- a

- b (paragraph 1)
  
  b (paragraph 2)

<!-- end: BulletList(loose=True) -->

# BulletList, implicit loose (paragraph, list)

<!-- start: BulletList(loose=True) -->
- a

- b (paragraph)
  
  <!-- start: BulletList(loose=False) -->
  - b1
  - b2
  - b3
  <!-- end: BulletList(loose=False) -->

<!-- end: BulletList(loose=True) -->

# BulletList, implicit loose (nested list)

<!-- start: BulletList(loose=True) -->
- a

- <!-- start: BulletList(loose=False) -->
  - b1
  - b2
  - b3
  <!-- end: BulletList(loose=False) -->

<!-- end: BulletList(loose=True) -->

# BulletList, 4 elements

<!-- start: BulletList(loose=True) -->
- a

- b

- c (not loose)
  <!-- start: BulletList(loose=False) -->
  - c1
  - c2
  - c3
  <!-- end: BulletList(loose=False) -->

- d (loose)
  <!-- start: BulletList(loose=True) -->
  - d1

  - d2

  - d3

  <!-- end: BulletList(loose=True) -->

<!-- end: BulletList(loose=True) -->

# NumberedList, 1 element

<!-- start: NumberedList(loose=True) -->
1. <p>a</p>

<!-- end: NumberedList(loose=True) -->

# NumberedList, implicit loose (paragraphs)

<!-- start: NumberedList(loose=True) -->
1. a

1. b (paragraph 1)
   
   b (paragraph 2)

<!-- end: NumberedList(loose=True) -->

# NumberedList, implicit loose (paragraph, list)

<!-- start: NumberedList(loose=True) -->
1. a

1. b (paragraph)
   
   <!-- start: NumberedList(loose=False) -->
   1. b1
   1. b2
   1. b3
   <!-- end: NumberedList(loose=False) -->

<!-- end: NumberedList(loose=True) -->

# NumberedList, implicit loose (nested list)

<!-- start: NumberedList(loose=True) -->
1. a

1. <!-- start: NumberedList(loose=False) -->
   1. b1
   1. b2
   1. b3
   <!-- end: NumberedList(loose=False) -->

<!-- end: NumberedList(loose=True) -->

# NumberedList, 4 elements

<!-- start: NumberedList(loose=True) -->
1. a

1. b

1. c (not loose)
   <!-- start: NumberedList(loose=False) -->
   1. c1
   1. c2
   1. c3
   <!-- end: NumberedList(loose=False) -->

1. d (loose)
   <!-- start: NumberedList(loose=True) -->
   1. d1

   1. d2

   1. d3

   <!-- end: NumberedList(loose=True) -->

<!-- end: NumberedList(loose=True) -->
