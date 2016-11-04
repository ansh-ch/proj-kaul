#lang racket
(require eopl/eopl)
(provide (all-defined-out))
(require "parser.rkt")
(require "ast.rkt")
(require "env-rec.rkt")
(require "store.rkt")
(init-store!)

(define id-parse
  (λ (e)
   (λ (b)
    (cases bind b
      [binding (bvar bast) (list bvar (new-ref (eval-ast bast e)))]
      ))))
      
(define separate
  (λ (ls res)
    (if (null? ls)
        (append res '())
        (if (null? res)
            (let ([x (first ls)])
               (separate (rest ls) (list (list (first x)) (list (second x)))))
            (let ([x (first ls)])
              (separate (rest ls) (list (append (first res) (list (first x))) (append (second res) (list (second x)))) ))
            ))))

(define fbind-fid
  (λ (fbins)
    (cases fbind fbins
      [ftied (fname formals body) fname])))

(define fbind-formals
  ( λ (fbins)
     (cases fbind fbins
      [ftied (fname formals body) formals])))

(define fbind-body
  (λ (fbins)
     (cases fbind fbins
      [ftied (fname formals body) body])))

(define eval-ast
  (λ (a e)
    (cases ast a
      [number (n) n]
      [boolean (b) b]
      [var-ref (var) 
               (match (lookup-env e var)
                 [(? number? num) (get-ref num)]
                 [(? proc? ls) ls]
               )]
      [ifte (test then else)
            (let ([tv (eval-ast test e)])
                (if (boolean? tv)
                    (cond
                      [(equal? tv #t) (eval-ast then e)]
                      [(equal? tv #f) (eval-ast else e)]
                      )
                    (error 'eval-ast-test "test not bool")
                    ))]
      [assume (bin body) (let ([x (separate (map (id-parse e) bin) '())])
                           (eval-ast body (extended-env (first x) (second x) e)))]
      [function (argz body) (closure argz body e)]
      [recfun (fbins body) 
              (let ([fids (map fbind-fid fbins)]
                    [lformals (map fbind-formals fbins)]
                    [bodies (map fbind-body fbins)])
                (letrec
                    ([cls (map (λ (formals body)
                                 (rec-closure (λ () (closure formals body new-env)))) lformals bodies)]
                     [store-cls (map new-ref cls)]
                     [new-env (rec-env (λ () (extended-env fids store-cls e)))])
                  (eval-ast body new-env)))]
     
      
      [prim-app (rator rands)
                (let ([args (map (λ(a) (eval-ast a e)) rands)]
                      [proc (eval-ast rator e)])
                  (if (proc? proc)
                      (apply-proc proc args)                     
                      proc))
                ]
      ;;(error '-------- "not procedure")
      [assign (var val) (set-ref (lookup-env e var) (eval-ast val e))]
      [seq (bods) (last (map-seq bods e))]
      [else (error 'have_to_rectify)]
      )))

(define map-seq
  (λ (bud e)
    (if (eq? bud '())
        '()
        (cons (eval-ast (first bud) e) (map-seq (rest bud) e)))))
    
(define apply-proc
  (λ (p args)
    (cases proc p
      [primitive (op sig)
                 (if (equal? (length args) (length sig))
                     (if (andmap (λ (s a) (s a)) sig args)
                         (apply op args)
                         (error '---- "arguments type error"))
                     (error '---- "arrity mismatch"))]
      [closure (formals body env) (eval-ast body (extended-env formals (map new-ref args) env))]
      [rec-closure (thunk)
                   (apply-proc (thunk) args)]
      )))