from src.validation import Validator

validator = Validator()


def test_correct_clothes_name_1():
    assert validator.check_clothes_name('Футболка') == True


def test_correct_clothes_name_2():
    assert validator.check_clothes_name('T-shirt') == True


def test_correct_clothes_name_3():
    assert validator.check_clothes_name('Джинсы') == True


def test_correct_clothes_name_4():
    assert validator.check_clothes_name('Платье') == True


def test_correct_clothes_name_5():
    assert validator.check_clothes_name('Jacket') == True


def test_correct_clothes_name_6():
    assert validator.check_clothes_name('TShirt') == True


def test_correct_clothes_name_7():
    assert validator.check_clothes_name('ПлатьеВечернее') == True


def test_correct_clothes_name_8():
    assert validator.check_clothes_name('Платье вечернее') == True


def test_correct_clothes_name_9():
    assert validator.check_clothes_name('T shirt') == True


def test_correct_clothes_name_10():
    assert validator.check_clothes_name('Платье-вечернее') == True


def test_correct_clothes_name_11():
    assert validator.check_clothes_name('Футболка с принтом') == True


def test_incorrect_clothes_name_1():
    assert validator.check_clothes_name('') == False


def test_incorrect_clothes_name_2():
    assert validator.check_clothes_name('Футболка 123') == False


def test_incorrect_clothes_name_3():
    assert validator.check_clothes_name('T-shirt!') == False


def test_incorrect_clothes_name_4():
    assert validator.check_clothes_name(' Футболка') == False


def test_incorrect_clothes_name_5():
    assert validator.check_clothes_name('Футболка 1') == False


def test_incorrect_clothes_name_6():
    assert validator.check_clothes_name('123') == False


def test_incorrect_clothes_name_7():
    assert validator.check_clothes_name('Футболка@') == False


def test_incorrect_clothes_name_8():
    assert validator.check_clothes_name(' T-shirt') == False
