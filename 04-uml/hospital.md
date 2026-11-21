# Exo 1 - Hospital Management System 🏥

Exercise: https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb (slide 68). Code: [`hospital.py`](hospital.py).

## Task 1 - basic class diagram

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

## Task 2 + 3 - full class diagram

My choices:
- `User` is an abstract superclass (id, name, password, login/logout), Patient, Doctor and Organizer inherit from it
- `Payment` is abstract and each payment type overrides `process()` (polymorphism, it's the Strategy pattern)
- composition `HealthProblem *-- Prescription`: a prescription doesn't exist without its problem
- aggregation `Patient o-- HealthProblem`: the patient keeps a history of his problems
- `ProblemStatus` is an enum (PENDING, IN_REVIEW, RESOLVED), and I added timestamps

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

## Task 2 - sequence: a patient submits a problem, gets a prescription and pays

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

## Task 3 - system sequence diagrams

### 1. Patient registration (organizer creates a new member)

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

### 2. Consultation flow (problem -> prescription delivered)

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

### 3. Payment processing (patient pays, organizer forwards to doctor)

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

1. **Patient consulting multiple doctors?** Each HealthProblem is assigned to one doctor, so a patient with several problems can see several doctors. If we want several doctors on the same problem, we could add a `Consultation` class between HealthProblem and Doctor (with `1..*` on the doctor side).
2. **Reusable prescriptions?** A prescription stays linked to its problem but it has a reference to the previous one (`previous`), so we keep the history and a renewal is just a new prescription pointing to the old one. For real reusable ones we could have a `PrescriptionTemplate` class.
3. **Design pattern for the payment?** Strategy: each payment type is a class with its own `process()`. We could also use a Factory to create the right one from "check" / "cash" / "card".
4. **Data integrity for payments?** Use database transactions (payment + forwarding succeed or fail together), check the amount matches the prescription fee, and have a `forwarded` flag so a payment can't be forwarded twice. Keeping a log with timestamps also helps.
