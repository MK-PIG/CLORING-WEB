from src.validation import Validator

validator = Validator()


def test_correct_clothes_description_1():
    assert validator.check_clothes_description('Красивая вещь') == True


def test_correct_clothes_description_2():
    assert validator.check_clothes_description('Beautiful item') == True


def test_correct_clothes_description_3():
    assert validator.check_clothes_description('В отличном состоянии') == True


def test_correct_clothes_description_4():
    assert validator.check_clothes_description(
        'In excellent condition') == True


def test_correct_clothes_description_5():
    assert validator.check_clothes_description('Носил один раз') == True


def test_correct_clothes_description_6():
    assert validator.check_clothes_description('Worn once') == True


def test_correct_clothes_description_7():
    assert validator.check_clothes_description(
        'Платье вечернее длинное') == True


def test_correct_clothes_description_8():
    assert validator.check_clothes_description('Evening dress long') == True


def test_correct_clothes_description_9():
    assert validator.check_clothes_description('Вещь-мечта') == True


def test_correct_clothes_description_10():
    assert validator.check_clothes_description('Dream-item') == True


def test_correct_clothes_description_11():
    assert validator.check_clothes_description(
        'Очень красивая и стильная вещь для особых случаев') == True


def test_incorrect_clothes_description_1():
    assert validator.check_clothes_description('') == False


def test_incorrect_clothes_description_2():
    assert validator.check_clothes_description('Красивая вещь 123') == False


def test_incorrect_clothes_description_3():
    assert validator.check_clothes_description('Beautiful!') == False


def test_incorrect_clothes_description_4():
    assert validator.check_clothes_description(' Красивая вещь') == False


def test_incorrect_clothes_description_5():
    assert validator.check_clothes_description('Вещь 1') == False


def test_incorrect_clothes_description_6():
    assert validator.check_clothes_description('123') == False


def test_incorrect_clothes_description_7():
    assert validator.check_clothes_description('Красивая@') == False


def test_incorrect_clothes_description_8():
    assert validator.check_clothes_description(' Beautiful') == False
