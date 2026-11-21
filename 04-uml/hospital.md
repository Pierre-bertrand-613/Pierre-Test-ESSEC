# Exo 1 - Hospital Management System 🏥

Énoncé : https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb (slide 68). Implémentation : [`hospital.py`](hospital.py).

## Task 1 : diagramme de classes de base

```mermaid
classDiagram
    class Patient {
        -id: int
        -name: str
        -password: str
        -email: str
        +post_problem(description) HealthProblem
        +pay(prescription, method) Payment
        +view_prescriptions() list
    }
    class Organizer {
        -id: int
        -name: str
        -password: str
        +consult_doctor(problem, doctor)
        +send_prescription(prescription, patient)
        +forward_payment(payment, doctor)
    }
    class Doctor {
        -id: int
        -name: str
        -password: str
        -speciality: str
        +write_prescription(problem) Prescription
        +receive_payment(amount)
    }
    Patient "1..*" -- "1" Organizer : submits problems to
    Organizer "1" -- "1..*" Doctor : consults
    Doctor "1" -- "0..*" Patient : treats
```

## Task 2 + 3 : diagramme de classes complet

Choix de modélisation :
- `User` est une **superclasse abstraite** (id, name, password, login/logout). `Patient`, `Doctor` et `Organizer` en héritent.
- `Payment` est **abstraite**, et le mode de paiement est modélisé par **polymorphisme** (pattern **Strategy**) : `CheckPayment`, `CashPayment` et `CreditCardPayment` redéfinissent `process()`.
- **Composition** `HealthProblem *-- Prescription` : une prescription n'existe pas sans le problème qu'elle résout.
- **Agrégation** `Patient o-- HealthProblem` : l'historique du patient regroupe ses problèmes.
- `ProblemStatus` est une énumération (PENDING, IN_REVIEW, RESOLVED) ; chaque objet a un timestamp.

```mermaid
classDiagram
    class User {
        <<abstract>>
        #id: int
        #name: str
        #password_hash: str
        -logged_in: bool
        +login(password) bool
        +logout()
    }
    class Patient {
        -problems: list~HealthProblem~
        +post_problem(description) HealthProblem
        +pay(prescription, payment) Payment
        +past_prescriptions() list~Prescription~
    }
    class Doctor {
        -speciality: str
        -earnings: float
        +write_prescription(problem, content, fee) Prescription
        +receive_payment(amount)
    }
    class Organizer {
        +register_member(kind, name, password) User
        +assign_doctor(problem, doctor)
        +send_prescription(problem)
        +forward_payment(payment)
    }
    class HealthProblem {
        -id: int
        -description: str
        -status: ProblemStatus
        -created_at: datetime
        +set_status(status)
    }
    class ProblemStatus {
        <<enumeration>>
        PENDING
        IN_REVIEW
        RESOLVED
    }
    class Prescription {
        -id: int
        -content: str
        -fee: float
        -created_at: datetime
        -previous: Prescription
    }
    class Payment {
        <<abstract>>
        -amount: float
        -paid_at: datetime
        -forwarded: bool
        +process()* str
    }
    class CheckPayment {
        -check_number: str
        +process() str
    }
    class CashPayment {
        +process() str
    }
    class CreditCardPayment {
        -card_number: str
        +process() str
    }

    User <|-- Patient
    User <|-- Doctor
    User <|-- Organizer
    Payment <|-- CheckPayment
    Payment <|-- CashPayment
    Payment <|-- CreditCardPayment

    Patient "1" o-- "0..*" HealthProblem : posts
    HealthProblem --> ProblemStatus
    HealthProblem "1" *-- "0..1" Prescription : solved by
    Doctor "0..1" <-- "0..*" HealthProblem : assigned to
    Doctor "1" -- "0..*" Prescription : writes
    Prescription "0..1" --> "0..1" Prescription : previous
    Patient "1" -- "0..*" Payment : makes
    Payment "1" --> "1" Prescription : pays for
    Organizer "1" -- "0..*" Payment : forwards
```

## Task 2 : séquence « un patient soumet un problème, reçoit une prescription et paie »

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as Platform
    actor O as Organizer
    actor D as Doctor

    P->>S: post_problem(description)
    S-->>O: new problem (PENDING)
    O->>S: assign_doctor(problem, doctor)
    S-->>D: problem to review (IN_REVIEW)
    D->>S: write_prescription(problem, content, fee)
    O->>S: send_prescription(problem)
    S-->>P: prescription
    P->>S: pay(prescription, CreditCardPayment)
    S->>S: payment.process()
    O->>S: forward_payment(payment)
    S-->>D: receive_payment(fee)
    S-->>P: problem RESOLVED
```

## Task 3 : diagrammes de séquence système

### 1. Inscription d'un patient (l'Organizer crée un membre)

```mermaid
sequenceDiagram
    actor O as Organizer
    participant S as System
    O->>S: login(password)
    S-->>O: ok
    O->>S: register_member("patient", name, password)
    S->>S: generate member id
    S->>S: hash password
    S-->>O: Patient(id)
    O-->>O: send id + password to the new member
```

### 2. Consultation : de la soumission du problème à la livraison de la prescription

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    actor O as Organizer
    actor D as Doctor
    P->>S: post_problem(description)
    S-->>P: HealthProblem(status=PENDING)
    O->>S: assign_doctor(problem, doctor)
    S-->>O: status=IN_REVIEW
    D->>S: write_prescription(problem, content, fee)
    S->>S: link previous prescription of the patient
    S-->>D: Prescription(id)
    O->>S: send_prescription(problem)
    S-->>P: Prescription
```

### 3. Paiement : le patient paie, l'Organizer reverse au Doctor

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    participant Pay as Payment (Check / Cash / CreditCard)
    actor O as Organizer
    actor D as Doctor
    P->>S: pay(prescription, payment)
    S->>Pay: process()
    alt payment accepted
        Pay-->>S: "paid"
        S-->>P: receipt, problem RESOLVED
        O->>S: forward_payment(payment)
        S->>D: receive_payment(amount)
        S->>S: payment.forwarded = True
    else payment refused
        Pay-->>S: error
        S-->>P: payment failed, retry
    end
```

## Questions

1. **Un patient qui consulte plusieurs médecins ?** Chaque `HealthProblem` est assigné à un `Doctor` (0..1). Un patient qui a plusieurs problèmes peut donc avoir plusieurs médecins. Pour plusieurs médecins sur *un même* problème, on ajoute une classe d'association `Consultation` (problem, doctor, date, avis), avec une multiplicité `1..*` côté docteur.
2. **Des prescriptions réutilisables ?** Une prescription reste liée au problème qui l'a créée (composition), mais elle référence la précédente (`previous`) : on garde l'historique et un renouvellement crée une nouvelle prescription qui pointe vers l'ancienne. Pour de vraies prescriptions-types, on séparerait `PrescriptionTemplate` (réutilisable) et `Prescription` (instance datée pour un patient).
3. **Quel pattern pour le paiement ?** **Strategy** : chaque mode de paiement est une classe interchangeable qui implémente `process()`. On peut y ajouter une **Factory** pour créer la bonne stratégie à partir de `"check"`, `"cash"` ou `"card"`.
4. **Intégrité des paiements ?** Transactions atomiques en base (le paiement et le reversement réussissent ou échouent ensemble), clé d'idempotence pour ne pas payer deux fois, un flag `forwarded` qui empêche de reverser deux fois, un journal d'audit horodaté, et la validation du montant par rapport au `fee` de la prescription.
