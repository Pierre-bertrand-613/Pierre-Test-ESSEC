import pytest

import abcd_records as abcd
import hospital as h


def test_hospital_full_workflow():
    organizer = h.Organizer("Admin", "admin")
    patient = organizer.register_member("patient", "Pierre", "pwd")
    doctor = organizer.register_member("doctor", "Dr X", "pwd", speciality="GP")
    assert patient.login("pwd") and not doctor.login("wrong")

    problem = patient.post_problem("Fever")
    assert problem.status is h.ProblemStatus.PENDING
    organizer.assign_doctor(problem, doctor)
    assert problem.status is h.ProblemStatus.IN_REVIEW

    doctor.write_prescription(problem, "Rest", fee=30)
    prescription = organizer.send_prescription(problem)
    payment = h.CashPayment(30)
    patient.pay(prescription, payment)
    organizer.forward_payment(payment)

    assert problem.status is h.ProblemStatus.RESOLVED
    assert doctor.earnings == 30
    with pytest.raises(ValueError):
        organizer.forward_payment(payment)   # cannot forward twice


def test_prescription_keeps_history():
    organizer = h.Organizer("Admin", "admin")
    patient = organizer.register_member("patient", "P", "pwd")
    doctor = organizer.register_member("doctor", "D", "pwd", speciality="GP")
    first = patient.post_problem("A")
    organizer.assign_doctor(first, doctor)
    p1 = doctor.write_prescription(first, "x", 10)
    second = patient.post_problem("B")
    organizer.assign_doctor(second, doctor)
    p2 = doctor.write_prescription(second, "y", 10)
    assert p2.previous is p1


def test_payment_polymorphism():
    payments = [h.CashPayment(10), h.CheckPayment(10, "42"), h.CreditCardPayment(10, "1" * 16)]
    assert all(isinstance(p.process(), str) for p in payments)


def test_royal_member_scenario():
    clerk = abcd.OrderProcessingClerk(abcd.DailyRecordsFile())
    royal = abcd.RoyalMember("P", "Paris")
    in_stock = abcd.CD("1", "A", "X", 15.0, stock=1)
    out_of_stock = abcd.CD("2", "B", "X", 20.0, stock=0)
    order, invoice, shipping = clerk.process_order(royal, [(in_stock, 1), (out_of_stock, 1)])
    assert invoice.amount == 31.5
    assert [l.item.title for l in shipping.lines] == ["A"]
    assert order.lines[1].backordered
    abcd.CollectionDeptClerk().collect_payment(invoice, abcd.Check(31.5, "1", "BNP"))
    assert invoice.paid and clerk.records.orders == [order]


def test_regular_member_cannot_order_unavailable():
    clerk = abcd.OrderProcessingClerk(abcd.DailyRecordsFile())
    regular = abcd.RegularMember("R", "Lyon")
    with pytest.raises(ValueError):
        clerk.process_order(regular, [(abcd.Tape("3", "C", "Y", 9.0, stock=0), 1)])


def test_non_member_gets_application():
    clerk = abcd.OrderProcessingClerk(abcd.DailyRecordsFile())
    assert isinstance(clerk.verify_membership(abcd.NonMember("N", "Nice")), abcd.MembershipApplication)
