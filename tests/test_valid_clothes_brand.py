from validation import Validator

validator = Validator()


def test_correct_clothes_brand_1():
    assert validator.check_clothes_brand('Zara') == True


def test_correct_clothes_brand_2():
    assert validator.check_clothes_brand('Nike') == True


def test_correct_clothes_brand_3():
    assert validator.check_clothes_brand('Nike') == True


def test_correct_clothes_brand_4():
    assert validator.check_clothes_brand('Adidas') == True


def test_correct_clothes_brand_5():
    assert validator.check_clothes_brand('Massimo Dutti') == True


def test_correct_clothes_brand_6():
    assert validator.check_clothes_brand('Tommy Hilfiger') == True


def test_correct_clothes_brand_7():
    assert validator.check_clothes_brand('Calvin Klein') == True


def test_correct_clothes_brand_8():
    assert validator.check_clothes_brand('Бренд') == True


def test_correct_clothes_brand_9():
    assert validator.check_clothes_brand('Русский бренд') == True


def test_correct_clothes_brand_10():
    assert validator.check_clothes_brand('Бренд-бренд') == True


def test_correct_clothes_brand_11():
    assert validator.check_clothes_brand('New Balance') == True

def test_correct_clothes_brand_12():
    assert validator.check_clothes_brand('H&M') == False



def test_incorrect_clothes_brand_1():
    assert validator.check_clothes_brand('') == False


def test_incorrect_clothes_brand_2():
    assert validator.check_clothes_brand('Zara 123') == False


def test_incorrect_clothes_brand_3():
    assert validator.check_clothes_brand('>Nike') == False


def test_incorrect_clothes_brand_4():
    assert validator.check_clothes_brand(' Zara') == False


def test_incorrect_clothes_brand_5():
    assert validator.check_clothes_brand('Adidas 1') == False


def test_incorrect_clothes_brand_6():
    assert validator.check_clothes_brand('123') == False


def test_incorrect_clothes_brand_7():
    assert validator.check_clothes_brand('Zara@') == False


def test_incorrect_clothes_brand_8():
    assert validator.check_clothes_brand(' Nike') == False

