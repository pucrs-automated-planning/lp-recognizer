(define (problem pb4)
(:domain blocks)
(:objects D A J I E G H B F C - block)
(:INIT (CLEAR C) (CLEAR F) (ONTABLE B) (ONTABLE H) (ON C G) (ON G E) (ON E I)
 (ON I J) (ON J A) (ON A B) (ON F D) (ON D H) (HANDEMPTY))
(:goal (and
<HYPOTHESIS>
))
)