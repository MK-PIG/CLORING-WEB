from validation import Validator

validator = Validator()


def test_correct_clothes_color_1():
    assert validator.check_clothes_color('Синий') == True


def test_correct_clothes_color_2():
    assert validator.check_clothes_color('Blue') == True


def test_correct_clothes_color_3():
    assert validator.check_clothes_color('Красный') == True


def test_correct_clothes_color_4():
    assert validator.check_clothes_color('Red') == True


def test_correct_clothes_color_5():
    assert validator.check_clothes_color('Зеленый') == True


def test_correct_clothes_color_6():
    assert validator.check_clothes_color('Green') == True


def test_correct_clothes_color_7():
    assert validator.check_clothes_color('Темно синий') == True


def test_correct_clothes_color_8():
    assert validator.check_clothes_color('Dark Blue') == True


def test_correct_clothes_color_9():
    assert validator.check_clothes_color('Светло-зеленый') == True


def test_correct_clothes_color_10():
    assert validator.check_clothes_color('Light-Green') == True


def test_correct_clothes_color_11():
    assert validator.check_clothes_color('Бежевый цвет') == True



def test_incorrect_clothes_color_1():
    assert validator.check_clothes_color('') == False


def test_incorrect_clothes_color_2():
    assert validator.check_clothes_color('Синий 123') == False


def test_incorrect_clothes_color_3():
    assert validator.check_clothes_color('Blue!') == False


def test_incorrect_clothes_color_4():
    assert validator.check_clothes_color(' Синий') == False


def test_incorrect_clothes_color_5():
    assert validator.check_clothes_color('Красный 1') == False


def test_incorrect_clothes_color_6():
    assert validator.check_clothes_color('123') == False


def test_incorrect_clothes_color_7():
    assert validator.check_clothes_color('Синий@') == False


def test_incorrect_clothes_color_8():
    assert validator.check_clothes_color(' Blue') == False

