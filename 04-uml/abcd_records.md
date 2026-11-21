# Exo 2 - ABCD Records 📼

Énoncé : https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb (slide 68). Implémentation : [`abcd_records.py`](abcd_records.py).

> Mermaid n'a pas de vrai diagramme de cas d'utilisation. Les cas d'utilisation sont donc représentés par des ovales dans un *flowchart*, le rectangle `ABCD Records System` joue le rôle de frontière du système, et les flèches en pointillés sont étiquetées `<<include>>` / `<<extend>>`.

## Level 1

### Task 1.1 : cas d'utilisation simples

```mermaid
flowchart LR
    M([👤 Member])
    C([👤 Order Processing Clerk])
    subgraph SYS[ABCD Records System]
        PO((Place Order))
        VM((Verify Membership))
        PR((Process Order))
        MP((Make Payment))
    end
    M --- PO
    M --- MP
    C --- VM
    C --- PR
```

### Task 1.2 : classes de base

```mermaid
classDiagram
    class Member {
        -member_id: int
        -name: str
        -address: str
        -email: str
        +place_order(items) Order
        +make_payment(order, payment)
    }
    class Order {
        -order_id: int
        -date: date
        -status: str
        -total: float
        +add_item(item, quantity)
        +compute_total() float
    }
    class OrderProcessingClerk {
        -employee_id: int
        -name: str
        +verify_membership(member) bool
        +process_order(order)
    }
    Member "1" -- "0..*" Order : places
    OrderProcessingClerk "1" -- "0..*" Order : processes
```

## Level 2

### Task 2.1 : cas d'utilisation complets

- `<<include>>` (obligatoire, toujours exécuté) : *Place Order* inclut *Verify Membership* et *Verify Item Availability*. *Process Order* inclut *Print Invoice* et *Print Shipping List*.
- `<<extend>>` (optionnel, sous condition) : *Apply Discount* et *Order Unavailable Items* étendent *Place Order*, seulement pour les membres Royal. *Send Membership Application* étend *Verify Membership* quand le client n'est pas membre.

```mermaid
flowchart LR
    M([👤 Member])
    R([👤 Royal Member])
    N([👤 Non-Member])
    OC([👤 Order Processing Clerk])
    CC([👤 Collection Dept Clerk])

    subgraph SYS[ABCD Records System]
        PO((Place Order))
        VM((Verify Membership))
        VA((Verify Item Availability))
        AD((Apply Discount))
        OU((Order Unavailable Items))
        SA((Send Membership Application))
        PR((Process Order))
        PI((Print Invoice))
        PS((Print Shipping List))
        MP((Make Payment))
    end

    R -->|is a| M
    M --- PO
    M --- MP
    N --- SA
    OC --- VM
    OC --- PR
    CC --- MP

    PO -. "&lt;&lt;include&gt;&gt;" .-> VM
    PO -. "&lt;&lt;include&gt;&gt;" .-> VA
    PR -. "&lt;&lt;include&gt;&gt;" .-> PI
    PR -. "&lt;&lt;include&gt;&gt;" .-> PS
    AD -. "&lt;&lt;extend&gt;&gt;" .-> PO
    OU -. "&lt;&lt;extend&gt;&gt;" .-> PO
    SA -. "&lt;&lt;extend&gt;&gt;" .-> VM
```

### Task 2.2 : classes complètes

```mermaid
classDiagram
    class Member {
        <<abstract>>
        #member_id: int
        #name: str
        #address: str
        +discount_rate()* float
        +can_order_unavailable()* bool
        +place_order() Order
    }
    class RoyalMember {
        +discount_rate() float = 0.10
        +can_order_unavailable() bool = True
    }
    class RegularMember {
        +discount_rate() float = 0
        +can_order_unavailable() bool = False
    }
    class NonMember {
        -name: str
        -address: str
    }
    class MembershipApplication {
        -applicant: NonMember
        -sent_at: date
    }
    class Item {
        <<abstract>>
        #code: str
        #title: str
        #artist: str
        #price: float
        #stock: int
        +is_available(qty) bool
    }
    class CD {
        -tracks: int
    }
    class Tape {
        -duration_min: int
    }
    class Order {
        -order_id: int
        -date: date
        -status: OrderStatus
        +add_line(item, qty)
        +subtotal() float
        +total() float
    }
    class OrderLine {
        -quantity: int
        -backordered: bool
        +line_total() float
    }
    class Invoice {
        -invoice_id: int
        -amount: float
        +print() str
    }
    class ShippingList {
        -lines: list
        +print() str
    }
    class Payment {
        <<abstract>>
        #amount: float
        #date: date
        +process()* str
    }
    class Cash
    class Check {
        -check_number: str
        -bank: str
    }
    class BankDraft {
        -draft_number: str
    }
    class OrderProcessingClerk {
        +verify_membership(customer) bool
        +process_order(order)
    }
    class CollectionDeptClerk {
        +collect_payment(invoice, payment)
    }
    class DailyRecordsFile {
        -date: date
        -orders: list
        +save(order)
    }

    Member <|-- RoyalMember
    Member <|-- RegularMember
    Item <|-- CD
    Item <|-- Tape
    Payment <|-- Cash
    Payment <|-- Check
    Payment <|-- BankDraft

    NonMember "1" -- "0..1" MembershipApplication : receives
    Member "1" -- "0..*" Order : places
    Order "1" *-- "1..*" OrderLine : contains
    OrderLine "0..*" --> "1" Item : refers to
    Order "1" -- "0..1" Invoice : billed by
    Order "1" -- "0..1" ShippingList : shipped with
    Invoice "1" -- "0..1" Payment : settled by
    OrderProcessingClerk "1" -- "0..*" Order : processes
    CollectionDeptClerk "1" -- "0..*" Payment : collects
    DailyRecordsFile "1" o-- "0..*" Order : records
```

#### Scénario : un membre Royal commande 2 CD (dont un indisponible) et paie par chèque

1. `RoyalMember.place_order()` crée un `Order` avec 2 `OrderLine` (CD A en stock, CD B en rupture).
2. Le clerk vérifie l'adhésion (OK) puis la disponibilité. CD B est indisponible, mais `can_order_unavailable()` renvoie `True`, donc la ligne est marquée `backordered`.
3. La remise Royal de 10 % est appliquée. L'`Invoice` reprend le total, la `ShippingList` ne contient que le CD A.
4. Le `Collection Dept Clerk` encaisse un `Check` et la commande est enregistrée dans le `DailyRecordsFile`.

Ce scénario est exécuté dans `abcd_records.py` (bloc `__main__`).

## Level 3 : diagrammes de séquence

### 1. Traitement complet d'une commande

```mermaid
sequenceDiagram
    actor M as Member
    actor OC as Order Clerk
    participant O as Order
    participant I as Item
    participant R as DailyRecordsFile
    actor CC as Collection Clerk
    M->>OC: place order (items)
    OC->>OC: verify_membership(member)
    OC->>O: create Order(member)
    loop for each item
        OC->>I: is_available(qty)
        I-->>OC: true / false
        OC->>O: add_line(item, qty, backordered?)
    end
    OC->>O: total() (discount applied)
    OC->>OC: print Invoice + ShippingList
    OC->>R: save(order)
    OC-->>M: Invoice
    M->>CC: payment
    CC->>CC: collect_payment(invoice, payment)
    CC-->>M: receipt
```

### 2. Vérification de l'adhésion (succès et échec)

```mermaid
sequenceDiagram
    actor C as Customer
    actor OC as Order Clerk
    participant DB as Members DB
    C->>OC: place order
    OC->>DB: find(customer)
    alt is a member
        DB-->>OC: Member
        OC-->>C: order accepted
    else not a member
        DB-->>OC: not found
        OC->>OC: create MembershipApplication
        OC-->>C: send membership application form
    end
```

### 3. Paiement (tous types)

```mermaid
sequenceDiagram
    actor M as Member
    actor CC as Collection Clerk
    participant P as Payment
    participant Inv as Invoice
    M->>CC: pay(invoice, method)
    alt Cash
        CC->>P: Cash(amount).process()
    else Check
        CC->>P: Check(amount, number, bank).process()
    else Bank Draft
        CC->>P: BankDraft(amount, number).process()
    end
    P-->>CC: confirmation
    CC->>Inv: mark as paid
    CC-->>M: receipt
```

### 4. Réapprovisionnement pour les membres Royal

```mermaid
sequenceDiagram
    actor R as Royal Member
    actor OC as Order Clerk
    participant I as Item
    participant S as Supplier
    R->>OC: order unavailable item
    OC->>I: is_available(qty)
    I-->>OC: false
    OC->>OC: can_order_unavailable(R)? true
    OC->>S: reorder(item, qty) (priority)
    OC-->>R: line backordered, priority delivery
    S-->>I: restock(qty)
    I-->>OC: item available
    OC-->>R: ship backordered item
```
