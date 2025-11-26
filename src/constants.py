from src.validation import Validator

validator = Validator()

"""['clothes_name', 'clothes_category', 'clothes_size',
                        'clothes_condition', 'clothes_brand', 'clothes_material',
                        'clothes_color', 'clothes_description']
    """

VALIDATOR_FUNC: dict = {
    'clothes_name': validator.check_clothes_name,
    'clothes_brand': validator.check_clothes_brand,
    'clothes_material': validator.check_clothes_material,
    'clothes_color': validator.check_clothes_color,
    'clothes_description': validator.check_clothes_description
}
