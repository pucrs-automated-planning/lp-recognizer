(define (problem pb4)
(:domain blocks)
(:objects D A J I E G H B F C - block)
(:INIT (CLEAR C) (CLEAR F) (ONTABLE B) (ONTABLE H) (ON C G) (ON G E) (ON E I)
 (ON I J) (ON J A) (ON A B) (ON F D) (ON D H) (HANDEMPTY))
(:goal (and
(ON C B) (ON B D) (ON D F) (ON F I) (ON I A) (ON A H) (ON H J) (ON J G) (ON G E)
))
)