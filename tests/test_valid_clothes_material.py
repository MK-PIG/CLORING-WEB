from validation import Validator

validator = Validator()


def test_correct_clothes_material_1():
    assert validator.check_clothes_material('Хлопок') == True


def test_correct_clothes_material_2():
    assert validator.check_clothes_material('Cotton') == True


def test_correct_clothes_material_3():
    assert validator.check_clothes_material('Шерсть') == True


def test_correct_clothes_material_4():
    assert validator.check_clothes_material('Silk') == True


def test_correct_clothes_material_5():
    assert validator.check_clothes_material('Полиэстер') == True



def test_correct_clothes_material_7():
    assert validator.check_clothes_material('Хлопок 34% шерсть 66%') == True


def test_correct_clothes_material_8():
    assert validator.check_clothes_material('Cotton Silk') == True


def test_correct_clothes_material_9():
    assert validator.check_clothes_material('Хлопок-шерсть') == True


def test_correct_clothes_material_10():
    assert validator.check_clothes_material('Cotton-Silk') == True


def test_correct_clothes_material_11():
    assert validator.check_clothes_material('Натуральный хлопок') == True


def test_correct_clothes_material_12():
    assert validator.check_clothes_material('Хлопок 100%') == True



def test_incorrect_clothes_material_1():
    assert validator.check_clothes_material('') == False


def test_incorrect_clothes_material_3():
    assert validator.check_clothes_material('Cotton!') == False


def test_incorrect_clothes_material_4():
    assert validator.check_clothes_material(' Хлопок') == False


def test_incorrect_clothes_material_5():
    assert validator.check_clothes_material('Шерсть 1') == False


def test_incorrect_clothes_material_6():
    assert validator.check_clothes_material('123') == False


def test_incorrect_clothes_material_7():
    assert validator.check_clothes_material('Хлопок@') == False


def test_incorrect_clothes_material_8():
    assert validator.check_clothes_material(' Cotton') == False

