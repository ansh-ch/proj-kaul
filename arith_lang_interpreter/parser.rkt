#lang racket
(require "ast.rkt")
(require eopl/eopl)
(provide (all-defined-out))

(define help_the_verse
  (λ (param forest)
    (normal_bind (cons param (cons forest '())))))

(define funcbind
  (λ (bflock)
    (match bflock
      [(list f formals body) (ftied f formals (parse body))])))

(define normal_bind
  (λ (nbind)
    (match nbind
      [(list (? id? id) rest) (binding id (parse rest))])))
    
(define parse
  (λ (rose)
    (match rose
      [(? number? n) (number n)]
      [(? boolean? b) (boolean b)]
      [(list 'let bin rest) (assume (map normal_bind bin) (parse rest))]
      [(list 'ifte test then else) (ifte (parse test) (parse then) (parse else))]
      [(list (list 'function param body) rest ...) (assume (map help_the_verse param rest) (parse body)) ]
      [(list 'fn (list param ...) rest) (function param (parse rest))]
      [(list 'recursive bindlist body) (recfun (map funcbind bindlist) (parse body)) ]
      [(list 'assign var val) (assign var (parse val))]
      [(list 'seq rest ...) (seq (map parse rest))]
      [(? id? id) (var-ref id)]
      [(list (? op? op) rest ...) (prim-app (parse op) (map parse rest))]
      )))