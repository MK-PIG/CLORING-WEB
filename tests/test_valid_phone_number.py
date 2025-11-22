from src.validation import Validator
validator = Validator()


def test_correct_phone_number_1():
    assert validator.check_phone_number_correction('+79846870234') == True


def test_correct_phone_number_2():
    assert validator.check_phone_number_correction('89846870234') == True


def test_correct_phone_number_3():
    assert validator.check_phone_number_correction('79846870234') == True


def test_correct_phone_number_4():
    assert validator.check_phone_number_correction('9846870234') == True


def test_incorrect_phone_number_1():
    assert validator.check_phone_number_correction('') == False


def test_incorrect_phone_number_2():
    assert validator.check_phone_number_correction(
        '593205829901924342342432423423124234353') == False


def test_incorrect_phone_number_3():
    assert validator.check_phone_number_correction('880033535351') == False


def test_incorrect_phone_number_4():
    assert validator.check_phone_number_correction('-88003553535') == False


def test_incorrect_phone_number_5():
    assert validator.check_phone_number_correction('88003!553535') == False


def test_incorrect_phone_number_6():
    assert validator.check_phone_number_correction('что-то') == False


def test_incorrect_phone_number_7():
    assert validator.check_phone_number_correction('something') == False


def test_incorrect_phone_number_8():
    assert validator.check_phone_number_correction(
        '+7 (985)-677-23-41') == False
