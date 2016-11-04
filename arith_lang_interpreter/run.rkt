#lang racket
(require eopl/eopl)
(provide (all-defined-out))
(require "parser.rkt")
(require "eval-ast.rkt")
(require "env-rec.rkt")
 
(define *global-env*
  (extended-env '(+ - * / < > <= >= = != 0? eq?)
                (list (primitive + (list number? number?))
                      (primitive - (list number? number?))
                      (primitive * (list number? number?))
                      (primitive / (list number? number?))
                      (primitive < (list number? number?))
                      (primitive > (list number? number?))
                      (primitive <= (list number? number?))
                      (primitive >= (list number? number?))
                      (primitive = (list number? number?))
                      (primitive (λ(x y) (not (equal? x y))) (list number? number?))
                      (primitive (λ (x) (zero? x)) (list number?))
                      (primitive = (list number? number?))) 
                (empty-env '())))

(define run
  (λ (ls)
    (eval-ast (parse ls) *global-env*)))