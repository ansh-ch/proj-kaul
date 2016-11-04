#lang racket
(require eopl/eopl)
(provide (all-defined-out))

(define empty-store (lambda () '()))

(define the-store 'nothing)

(define init-store!
  (lambda ()
    (set! the-store (empty-store))))

(define get-store
  (lambda () the-store))


;; ????( What for)
(define reference?
  (lambda (v)
    (integer? v)))

(define new-ref
  (lambda (val)
    (let ([next-ref (length the-store)])
      (set! the-store (append  the-store (list val)))
      next-ref)))

(define get-ref
  (lambda (ref)
    (list-ref the-store ref)))
;;(list-ref the-store ref)
;(report-invalid-reference ref the-store)) instead of error
(define set-ref
  (lambda (ref val)
    (set! the-store
          (letrec
              ([setref-inner
                (lambda (store1 ref1)
                  (cond
                    [(null? store1)
                     (error "Invalid reference store")]
                    [(zero? ref1)
                     (cons val (cdr store1))]
                    [else
                     (cons
                      (car store1)
                      (setref-inner
                       (cdr store1) (- ref1 1)))]))])
            (setref-inner the-store ref)))))

