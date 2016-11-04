#lang racket
(require "ast.rkt")
(require eopl/eopl)
(provide (all-defined-out))

(define-datatype proc proc?
  [primitive (op procedure?) (sig (list-of procedure?))]
  [closure (formals (list-of id?)) (body ast?) (e env?)]
  [rec-closure (thunk procedure?)]
  )

(define den
  (lambda (d)
    (or (procedure? d) (number? d) (boolean? d) (proc? d))))

(define-datatype env env?
  [empty-env (emp null?)]
  [extended-env (vars (list-of id?)) (vals (list-of den)) (outer-env env?)]
  [rec-env (thunk procedure?)])


(define list-indice
  (λ (lis var temp)
    (if (null? lis)
        -1
        (if (equal? (first lis) var)
            temp
            (list-indice (rest lis) var (+ 1 temp))))))
   
   
(define lookup-env
  (λ (e x)
    (cases env e
      [extended-env (vars vals outer-env)
                    (let ([j (list-indice vars x 0)])
                      (if (= j -1)
                          (lookup-env outer-env x)
                          (list-ref vals j)))]
      [rec-env (thunk) (lookup-env (thunk) x)]
      [empty-env (error 'lookup-env)]
      )))