# Exo 2 - ABCD Records 📼

Exercise: https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb (slide 68). Code: [`abcd_records.py`](abcd_records.py).

> Mermaid doesn't have real use case diagrams, so I used a flowchart: use cases are ovals, the `ABCD Records System` box is the system boundary and the dotted arrows are `<<include>>` / `<<extend>>`.

## Level 1

### Task 1.1 - simple use case diagram

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

### Task 1.2 - basic class diagram

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

### Task 2.1 - full use case diagram

- `<<include>>` (always happens): Place Order includes Verify Membership and Verify Item Availability, Process Order includes Print Invoice and Print Shipping List
- `<<extend>>` (only sometimes): Apply Discount and Order Unavailable Items extend Place Order (only for Royal members), Send Membership Application extends Verify Membership (when the customer is not a member)

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

### Task 2.2 - full class diagram

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

#### Scenario: a Royal member orders 2 CDs (one unavailable) and pays by check

1. `RoyalMember.place_order()` creates an Order with 2 OrderLines (CD A in stock, CD B out of stock)
2. The clerk checks the membership (ok) and the availability. CD B is not available but Royal members can order it anyway, so the line is `backordered`
3. The 10% Royal discount is applied, the Invoice has the total and the ShippingList only has CD A
4. The collection clerk takes the Check and the order is saved in the DailyRecordsFile

This scenario runs in the `__main__` of `abcd_records.py`.

## Level 3 - sequence diagrams

### 1. Complete order processing

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

### 2. Membership verification (success and failure)

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

### 3. Payment processing (all types)

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

### 4. Item reordering for Royal members

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
