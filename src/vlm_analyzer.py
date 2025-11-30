"""
Модуль для анализа изображений одежды с использованием FastVLM от Apple
"""
import base64
from typing import Dict, Optional
from src.logger import info_logger, er_logger

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    from PIL import Image
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    info_logger.warning("Transformers library not available. VLM analysis will be disabled.")

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    info_logger.warning("deep-translator not available. Using simple translation.")


class ClothesVLMAnalyzer:
    """Класс для анализа изображений одежды с помощью FastVLM"""
    
    def __init__(self):
        """Инициализация анализатора"""
        self.model = None
        self.processor = None
        self.device = None
        self.is_loaded = False
        # НЕ загружаем модель при инициализации - она загрузится при первом вызове analyze_image
    
    def _load_model(self):
        """Загрузка модели FastVLM"""
        try:
            print("=" * 50)
            print("Starting VLM model loading...")
            print("=" * 50)
            info_logger.info("Loading VLM model...")
            
            # Определяем устройство (GPU если доступен, иначе CPU)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            info_logger.info(f"Using device: {self.device}")
            print(f"Device: {self.device}")
            
            # Используем BLIP - простая и эффективная модель
            model_name = "Salesforce/blip-image-captioning-base"
            
            info_logger.info(f"Loading model: {model_name}")
            print(f"Loading model: {model_name}")
            print("This may take 1-2 minutes on first run (downloading ~900MB)...")
            
            print("Step 1/2: Loading processor...")
            self.processor = BlipProcessor.from_pretrained(model_name)
            print("✓ Processor loaded")
            
            print("Step 2/2: Loading model...")
            self.model = BlipForConditionalGeneration.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            print("✓ Model loaded")
            
            self.is_loaded = True
            info_logger.info("VLM model loaded successfully")
            print("=" * 50)
            print("VLM model ready!")
            print("=" * 50)
            
        except Exception as e:
            er_logger.error(f"Error loading VLM model: {e}")
            self.is_loaded = False
            raise
    
    def analyze_image(self, image_path: str) -> Optional[Dict[str, str]]:
        """
        Анализирует изображение одежды и возвращает характеристики
        
        Args:
            image_path: путь к изображению
            
        Returns:
            Словарь с характеристиками одежды или None в случае ошибки
        """
        # Загружаем модель при первом вызове (ленивая загрузка)
        if not self.is_loaded and TRANSFORMERS_AVAILABLE:
            try:
                self._load_model()
            except Exception as e:
                er_logger.error(f"Failed to load model: {e}")
                return None
        
        if not self.is_loaded:
            er_logger.warning("Model is not loaded. Returning empty result.")
            return None
        
        try:
            info_logger.info(f"Analyzing image: {image_path}")
            
            # Загружаем изображение
            image = Image.open(image_path).convert('RGB')
            
            # BLIP использует conditional generation
            # Сначала получаем общее описание
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            
            # Генерируем описание
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=100)
            
            # Декодируем результат
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            info_logger.info(f"Generated caption: {caption}")
            print(f"BLIP caption: {caption}")
            
            # Парсим описание и извлекаем данные
            parsed_data = self._parse_caption(caption)
            
            return parsed_data
            
        except Exception as e:
            er_logger.error(f"Error analyzing image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_caption(self, caption: str) -> Dict[str, str]:
        """
        Парсит описание от BLIP и извлекает данные об одежде
        
        Args:
            caption: текстовое описание от модели
            
        Returns:
            Словарь с извлеченными данными
        """
        caption_lower = caption.lower()
        
        # Словари для перевода
        category_keywords = {
            't-shirt': ('t-shirt', 'tee', 'tshirt', 't shirt'),  # Футболка - первый приоритет
            'shirt': ('shirt', 'blouse'),  # Рубашка - после футболки
            'jeans': ('jeans', 'denim'),
            'dress': ('dress',),
            'pants': ('pants', 'trousers'),
            'skirt': ('skirt',),
            'jacket': ('jacket', 'coat'),
            'shoes': ('shoes', 'boots', 'sneakers'),
        }
        
        colors = {
            'white': 'Белый',
            'black': 'Черный',
            'light blue': 'Голубой',
            'dark blue': 'Темно-синий',
            'blue': 'Синий',
            'red': 'Красный',
            'dark red': 'Темно-красный',
            'green': 'Зеленый',
            'dark green': 'Темно-зеленый',
            'yellow': 'Желтый',
            'gray': 'Серый',
            'grey': 'Серый',
            'brown': 'Коричневый',
            'pink': 'Розовый',
            'purple': 'Фиолетовый',
            'orange': 'Оранжевый',
            'beige': 'Бежевый',
        }
        
        materials = {
            'denim': 'Деним',
            'cotton': 'Хлопок',
            'leather': 'Кожа',
            'wool': 'Шерсть',
            'silk': 'Шелк',
            'linen': 'Лен',
            'polyester': 'Полиэстер',
            'nylon': 'Нейлон',
        }
        
        category_names_ru = {
            'jeans': 'Джинсы',
            'dress': 'Платье',
            'shirt': 'Рубашка',
            't-shirt': 'Футболка',
            'pants': 'Брюки',
            'skirt': 'Юбка',
            'jacket': 'Куртка',
            'shoes': 'Обувь',
        }
        
        # Определяем категорию (по порядку приоритета)
        category = ''
        
        # Специальная проверка для футболки (очень важно!)
        if any(word in caption_lower for word in ['t-shirt', 't - shirt', 'tshirt', 'tee shirt', ' tee ']):
            category = 't-shirt'
        elif 'shirt' in caption_lower and 't' not in caption_lower[:caption_lower.index('shirt')]:
            # Это рубашка только если нет "t" перед "shirt"
            category = 'shirt'
        else:
            # Остальные категории
            for cat, keywords in category_keywords.items():
                if cat in ['t-shirt', 'shirt']:
                    continue  # Уже проверили выше
                if any(word in caption_lower for word in keywords):
                    category = cat
                    break
        
        # Определяем доминирующий цвет
        color = ''
        
        # Разбиваем описание на части по позициям цветов
        color_positions = {}
        for eng in colors.keys():
            pos = caption_lower.find(eng)
            if pos >= 0:
                # Проверяем контекст - не связан ли цвет с деталью?
                context_after = caption_lower[pos:pos+len(eng)+20]
                
                # Если после цвета идут слова trim/collar/sleeve - это не основной цвет
                detail_words = ['trim', 'collar', 'sleeve', 'border', 'edge', 'cuff', 'neckline']
                is_detail = any(detail in context_after for detail in detail_words)
                
                if not is_detail:
                    color_positions[eng] = pos
        
        # Берем самый первый цвет (обычно это основной)
        if color_positions:
            first_color = min(color_positions.keys(), key=lambda x: color_positions[x])
            color = colors[first_color]
        
        # Определяем материал
        material = ''
        for eng, rus in materials.items():
            if eng in caption_lower:
                material = rus
                break
        
        # Если категория джинсы/деним - материал всегда деним
        if category == 'jeans' and not material:
            material = 'Деним'
        
        # Определяем состояние одежды
        condition = ''
        condition_keywords = {
            'new': ('new', 'brand new', 'unworn', 'pristine'),
            'excellent': ('excellent', 'perfect', 'like new', 'mint', 'great'),
            'good': ('good', 'nice', 'clean', 'well-kept'),
            'satisfactory': ('worn', 'used', 'old', 'vintage', 'ragged', 'faded', 'distressed')
        }
        
        for cond, keywords in condition_keywords.items():
            if any(word in caption_lower for word in keywords):
                condition = cond
                break
        
        # Если не определено состояние, ставим "good" по умолчанию
        if not condition:
            condition = 'good'
        
        # Генерируем название вещи
        clothes_name = ''
        if category:
            clothes_name = category_names_ru.get(category, '')
            if color:
                clothes_name = f"{color} {clothes_name.lower()}"
        
        # Переводим описание на русский
        description_ru = self._translate_description(caption, category, color)
        
        result = {
            'clothes_category': category,
            'clothes_color': color,
            'clothes_material': material,
            'clothes_brand': '',
            'clothes_description': description_ru,
            'clothes_name': clothes_name,
            'clothes_condition': condition  # Добавляем состояние
        }
        
        info_logger.info(f"Parsed caption data: {result}")
        return result
    
    def _translate_description(self, caption: str, category: str, color: str) -> str:
        """Перевод описания на русский - максимально улучшенный вариант"""
        
        result = caption.lower()
        
        # Сложные фразы (обрабатываем первыми - от длинных к коротким)
        complex_phrases = {
            # Полные предложения с контекстом
            'a woman in a red dress walking down the street': 'женщина в красном платье идет по улице',
            'a woman in a blue dress walking down the street': 'женщина в синем платье идет по улице',
            'a woman in a white dress walking down the street': 'женщина в белом платье идет по улице',
            'a woman in a black dress walking down the street': 'женщина в черном платье идет по улице',
            'a woman wearing a red dress': 'женщина в красном платье',
            'a woman wearing a blue dress': 'женщина в синем платье',
            'a woman wearing a white dress': 'женщина в белом платье',
            'a woman wearing a black dress': 'женщина в черном платье',
            'a woman wearing a white t-shirt': 'женщина в белой футболке',
            'a woman wearing a black t-shirt': 'женщина в черной футболке',
            'a woman wearing a blue t-shirt': 'женщина в синей футболке',
            'a woman wearing a red t-shirt': 'женщина в красной футболке',
            'a woman wearing a black shirt': 'женщина в черной рубашке',
            'a woman wearing a white shirt': 'женщина в белой рубашке',
            'a woman wearing blue jeans': 'женщина в синих джинсах',
            'a woman wearing black jeans': 'женщина в черных джинсах',
            'a man wearing a black t-shirt': 'мужчина в черной футболке',
            'a man wearing a white shirt': 'мужчина в белой рубашке',
            'a man wearing blue jeans': 'мужчина в синих джинсах',
            
            # Составные действия
            'walking down the street': 'идет по улице',
            'walking down a street': 'идет по улице',
            'walking on the sidewalk': 'идет по тротуару',
            'standing in front of a wall': 'стоит перед стеной',
            'standing in front of the wall': 'стоит перед стеной',
            'standing on the sidewalk': 'стоит на тротуаре',
            'standing in a room': 'стоит в комнате',
            'sitting on a bench': 'сидит на скамейке',
            'sitting on the floor': 'сидит на полу',
            'posing for a photo': 'позирует для фото',
            'posing for the camera': 'позирует для камеры',
            'looking at the camera': 'смотрит в камеру',
            
            # Описания одежды с деталями
            'with black trim': 'с черной окантовкой',
            'with white trim': 'с белой окантовкой',
            'with red trim': 'с красной окантовкой',
            'with blue trim': 'с синей окантовкой',
            'with a black collar': 'с черным воротником',
            'with a white collar': 'с белым воротником',
            'with long sleeves': 'с длинными рукавами',
            'with short sleeves': 'с короткими рукавами',
            'with pockets': 'с карманами',
            'with buttons': 'с пуговицами',
            'with a zipper': 'с молнией',
            'and black sleeves': 'и черными рукавами',
            'and white sleeves': 'и белыми рукавами',
            'and blue sleeves': 'и синими рукавами',
            'with stripes': 'в полоску',
            'with a pattern': 'с узором',
        }
        
        for eng, rus in sorted(complex_phrases.items(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(eng, rus)
        
        # Средние фразы (комбинации)
        phrases = {
            'wearing a': 'в',
            'wearing an': 'в',
            'walking down': 'идет по',
            'walking on': 'идет по',
            'standing in': 'стоит в',
            'standing on': 'стоит на',
            'sitting on': 'сидит на',
            'posing for': 'позирует для',
            'looking at': 'смотрит на',
            'in front of': 'перед',
            'next to': 'рядом с',
            'near the': 'около',
            'behind the': 'позади',
            'inside the': 'внутри',
            'outside the': 'снаружи',
        }
        
        for eng, rus in phrases.items():
            result = result.replace(eng, rus)
        
        # Артикли (убираем раньше других слов)
        result = result.replace(' a ', ' ')
        result = result.replace(' an ', ' ')
        result = result.replace(' the ', ' ')
        
        # Отдельные слова
        words = {
            # Предлоги и союзы
            ' and ': ' и ',
            ' with ': ' с ',
            ' in ': ' в ',
            ' on ': ' на ',
            ' for ': ' для ',
            ' of ': ' ',
            ' at ': ' у ',
            ' from ': ' из ',
            ' to ': ' к ',
            ' by ': ' у ',
            ' near ': ' около ',
            
            # Люди (с правильными окончаниями)
            'woman': 'женщина',
            'man': 'мужчина',
            'person': 'человек',
            'people': 'люди',
            'girl': 'девушка',
            'boy': 'юноша',
            'lady': 'дама',
            'gentleman': 'джентльмен',
            'child': 'ребенок',
            'children': 'дети',
            'adult': 'взрослый',
            'model': 'модель',
            
            # Действия (причастия и глаголы)
            'walking': 'идущий',
            'standing': 'стоящий',
            'sitting': 'сидящий',
            'wearing': 'носящий',
            'posing': 'позирующий',
            'looking': 'смотрящий',
            'smiling': 'улыбающийся',
            'holding': 'держащий',
            'carrying': 'несущий',
            'running': 'бегущий',
            'jumping': 'прыгающий',
            
            # Места и окружение
            'street': 'улица',
            'sidewalk': 'тротуар',
            'road': 'дорога',
            'path': 'дорожка',
            'pavement': 'тротуар',
            'room': 'комната',
            'store': 'магазин',
            'shop': 'магазин',
            'building': 'здание',
            'house': 'дом',
            'wall': 'стена',
            'floor': 'пол',
            'ceiling': 'потолок',
            'background': 'фон',
            'outdoor': 'улица',
            'outdoors': 'улица',
            'indoors': 'помещение',
            'park': 'парк',
            'garden': 'сад',
            'bench': 'скамейка',
            
            # Одежда - специфичные комбинации (цвет + предмет)
            'white t-shirt': 'белая футболка',
            'black t-shirt': 'черная футболка',
            'blue t-shirt': 'синяя футболка',
            'red t-shirt': 'красная футболка',
            'gray t-shirt': 'серая футболка',
            'green t-shirt': 'зеленая футболка',
            'white shirt': 'белая рубашка',
            'black shirt': 'черная рубашка',
            'blue shirt': 'синяя рубашка',
            'red shirt': 'красная рубашка',
            'blue jeans': 'синие джинсы',
            'black jeans': 'черные джинсы',
            'white jeans': 'белые джинсы',
            'red dress': 'красное платье',
            'blue dress': 'синее платье',
            'white dress': 'белое платье',
            'black dress': 'черное платье',
            'pink dress': 'розовое платье',
            'green dress': 'зеленое платье',
            'black pants': 'черные брюки',
            'white pants': 'белые брюки',
            'gray pants': 'серые брюки',
            'black skirt': 'черная юбка',
            'white skirt': 'белая юбка',
            'red skirt': 'красная юбка',
            'black jacket': 'черная куртка',
            'blue jacket': 'синяя куртка',
            'leather jacket': 'кожаная куртка',
            'denim jacket': 'джинсовая куртка',
            
            # Одежда - общее (виды)
            't-shirt': 'футболка',
            't - shirt': 'футболка',
            'tshirt': 'футболка',
            'tee shirt': 'футболка',
            'tee': 'футболка',
            'tank top': 'майка',
            'shirt': 'рубашка',
            'blouse': 'блузка',
            'top': 'топ',
            'jeans': 'джинсы',
            'denim pants': 'джинсы',
            'denim': 'джинса',
            'dress': 'платье',
            'gown': 'платье',
            'pants': 'брюки',
            'trousers': 'брюки',
            'skirt': 'юбка',
            'shorts': 'шорты',
            'jacket': 'куртка',
            'coat': 'пальто',
            'overcoat': 'пальто',
            'blazer': 'пиджак',
            'suit jacket': 'пиджак',
            'sweater': 'свитер',
            'pullover': 'пуловер',
            'hoodie': 'толстовка',
            'sweatshirt': 'толстовка',
            'cardigan': 'кардиган',
            'vest': 'жилет',
            'leggings': 'леггинсы',
            'stockings': 'чулки',
            'socks': 'носки',
            'shoes': 'туфли',
            'boots': 'ботинки',
            'sneakers': 'кроссовки',
            'sandals': 'сандалии',
            'heels': 'каблуки',
            'scarf': 'шарф',
            'hat': 'шляпа',
            'cap': 'кепка',
            'beanie': 'шапка',
            'gloves': 'перчатки',
            'tie': 'галстук',
            
            # Цвета (расширенные варианты)
            'light blue': 'голубой',
            'sky blue': 'небесно-голубой',
            'dark blue': 'темно-синий',
            'navy blue': 'темно-синий',
            'navy': 'темно-синий',
            'bright blue': 'ярко-синий',
            'pale blue': 'бледно-голубой',
            'dark red': 'темно-красный',
            'bright red': 'ярко-красный',
            'burgundy': 'бордовый',
            'maroon': 'бордовый',
            'crimson': 'малиновый',
            'dark green': 'темно-зеленый',
            'light green': 'светло-зеленый',
            'olive green': 'оливковый',
            'olive': 'оливковый',
            'lime green': 'салатовый',
            'light gray': 'светло-серый',
            'dark gray': 'темно-серый',
            'charcoal': 'угольно-серый',
            'silver': 'серебристый',
            'gold': 'золотой',
            'red': 'красный',
            'blue': 'синий',
            'white': 'белый',
            'black': 'черный',
            'green': 'зеленый',
            'yellow': 'желтый',
            'pink': 'розовый',
            'hot pink': 'ярко-розовый',
            'gray': 'серый',
            'grey': 'серый',
            'brown': 'коричневый',
            'tan': 'бежевый',
            'purple': 'фиолетовый',
            'violet': 'фиолетовый',
            'lavender': 'лавандовый',
            'orange': 'оранжевый',
            'beige': 'бежевый',
            'cream': 'кремовый',
            'ivory': 'слоновая кость',
            'khaki': 'хаки',
            'turquoise': 'бирюзовый',
            'cyan': 'голубой',
            'magenta': 'пурпурный',
            'multicolored': 'разноцветный',
            'colorful': 'яркий',
            
            # Детали одежды (расширенные)
            'trimmed': 'с окантовкой',
            'trim': 'окантовка',
            'trims': 'окантовка',
            'collar': 'воротник',
            'collared': 'с воротником',
            'sleeve': 'рукав',
            'sleeves': 'рукава',
            'long sleeve': 'длинный рукав',
            'short sleeve': 'короткий рукав',
            'sleeveless': 'без рукавов',
            'pocket': 'карман',
            'pockets': 'карманы',
            'button': 'пуговица',
            'buttons': 'пуговицы',
            'buttoned': 'застегнутый',
            'zipper': 'молния',
            'zip': 'молния',
            'belt': 'ремень',
            'belted': 'с ремнем',
            'logo': 'логотип',
            'print': 'принт',
            'printed': 'с принтом',
            'pattern': 'узор',
            'patterned': 'с узором',
            'embroidered': 'вышитый',
            'lace': 'кружево',
            'ruffles': 'рюши',
            'pleated': 'плиссированный',
            
            # Материалы
            'cotton': 'хлопок',
            'leather': 'кожа',
            'wool': 'шерсть',
            'silk': 'шелк',
            'satin': 'атлас',
            'velvet': 'бархат',
            'linen': 'лен',
            'polyester': 'полиэстер',
            'synthetic': 'синтетика',
            'knit': 'трикотаж',
            'knitted': 'вязаный',
            
            # Стили и узоры (расширенные)
            'striped': 'в полоску',
            'stripy': 'в полоску',
            'checkered': 'в клетку',
            'checked': 'в клетку',
            'plaid': 'в клетку',
            'polka dot': 'в горошек',
            'dotted': 'в горошек',
            'floral': 'цветочный',
            'flowered': 'в цветочек',
            'geometric': 'геометрический',
            'plain': 'однотонный',
            'solid': 'однотонный',
            'solid color': 'однотонный',
            'casual': 'повседневный',
            'formal': 'официальный',
            'business': 'деловой',
            'vintage': 'винтажный',
            'retro': 'ретро',
            'modern': 'современный',
            'classic': 'классический',
            'sporty': 'спортивный',
            'athletic': 'спортивный',
            'elegant': 'элегантный',
            'stylish': 'стильный',
            'fashionable': 'модный',
            'trendy': 'модный',
            'chic': 'шикарный',
            'bohemian': 'богемный',
            'boho': 'бохо',
            
            # Размер и крой
            'fitted': 'приталенный',
            'tight': 'обтягивающий',
            'loose': 'свободный',
            'baggy': 'мешковатый',
            'oversized': 'oversized',
            'slim': 'узкий',
            'skinny': 'очень узкий',
            'wide': 'широкий',
            'long': 'длинный',
            'short': 'короткий',
            'mini': 'мини',
            'maxi': 'макси',
            'midi': 'миди',
            
            # Состояние
            'new': 'новый',
            'old': 'старый',
            'worn': 'поношенный',
            'clean': 'чистый',
            'dirty': 'грязный',
            'stained': 'испачканный',
            'wrinkled': 'мятый',
            'ironed': 'глаженый',
            'torn': 'порванный',
            'ripped': 'порванный',
            'faded': 'выцветший',
            
            # Погода и сезон
            'summer': 'летний',
            'winter': 'зимний',
            'spring': 'весенний',
            'fall': 'осенний',
            'autumn': 'осенний',
            'warm': 'теплый',
            'cold': 'холодный',
            
            # Другое
            'photo': 'фото',
            'picture': 'фотография',
            'image': 'изображение',
            'camera': 'камера',
            'photography': 'фотография',
            'outfit': 'наряд',
            'clothing': 'одежда',
            'clothes': 'одежда',
            'apparel': 'одежда',
            'garment': 'предмет одежды',
            'style': 'стиль',
            'fashion': 'мода',
        }
        
        for eng, rus in words.items():
            result = result.replace(eng, rus)
        
        # Убираем множественные пробелы
        while '  ' in result:
            result = result.replace('  ', ' ')
        
        # Убираем пробелы перед точками и запятыми
        result = result.replace(' ,', ',').replace(' .', '.')
        
        result = result.strip()
        
        # Первая буква заглавная
        if result:
            result = result[0].upper() + result[1:]
        
        return result


# Глобальный экземпляр анализатора
_analyzer_instance = None


def get_analyzer() -> ClothesVLMAnalyzer:
    """Получить экземпляр анализатора (singleton)"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ClothesVLMAnalyzer()
    return _analyzer_instance
