from validation import Validator

validator = Validator()

def test_correct_email_1():
    assert validator.check_correction_email('some@mail.ru') == True


def test_correct_email_2():
    assert validator.check_correction_email(
        'fjhsdknfsxkjdhnkxfbsnkhk@mail.ru') == True


def test_incorrect_email_1():
    assert validator.check_correction_email('somemail.ru') == False


def test_incorrect_email_2():
    assert validator.check_correction_email(
        'uodfhlkfmvcjnhckmdnfuhgdcuhcdmfnhvjxgdmncggjmnhjjghdfkfjgdfnkjdfhgnkdfjbgdfhgndfkbgdfjkghdfbjhvbfdjkvhdfvbjdfnvhdfujvdfghdfigbdfvbdhjvbdjh@mail.ru') == False


def test_incorrect_email_3():
    assert validator.check_correction_email('#some@mail.ru') == False


def test_incorrect_email_4():
    assert validator.check_correction_email('so.m.e@mail.ru') == False


def test_incorrect_email_5():
    assert validator.check_correction_email('lalal@lalal@mail.ru') == False


def test_incorrect_email_6():
    assert validator.check_correction_email('') == False


def test_incorrect_email_7():
    assert validator.check_correction_email('some@mail......ru') == False
