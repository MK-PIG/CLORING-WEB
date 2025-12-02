"""
Модуль для анализа изображений одежды с использованием VLM (Vision Language Model)

Использует модель BLIP от Salesforce для генерации описаний изображений одежды.
Все результаты переводятся на русский язык с использованием расширенного словаря перевода.
Система генерирует несколько типов описаний для более точного определения характеристик одежды.
"""
import base64
import re
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


class ClothesVLMAnalyzer:
    """
    Класс для анализа изображений одежды с помощью VLM модели BLIP.
    
    Генерирует подробные описания одежды на русском языке, включая:
    - Цвет
    - Тип/категорию одежды  
    - Материал
    - Состояние
    - Подробное текстовое описание
    
    Использует несколько промптов для получения максимально точной информации.
    """
    
    CATEGORY_METADATA = {
        'jeans': {'name': 'Джинсы', 'gender': 'pl'},
        'dress': {'name': 'Платье', 'gender': 'neut'},
        'shirt': {'name': 'Рубашка', 'gender': 'fem'},
        't-shirt': {'name': 'Футболка', 'gender': 'fem'},
        'pants': {'name': 'Брюки', 'gender': 'pl'},
        'skirt': {'name': 'Юбка', 'gender': 'fem'},
        'jacket': {'name': 'Куртка', 'gender': 'fem'},
        'coat': {'name': 'Пальто', 'gender': 'neut'},
        'shoes': {'name': 'Обувь', 'gender': 'fem'},
        'blouse': {'name': 'Блузка', 'gender': 'fem'},
        'hoodie': {'name': 'Толстовка', 'gender': 'fem'},
        'sweater': {'name': 'Свитер', 'gender': 'masc'},
    }

    COLOR_FORMS = {
        'Белый': {'masc': 'Белый', 'fem': 'Белая', 'neut': 'Белое', 'pl': 'Белые'},
        'Черный': {'masc': 'Черный', 'fem': 'Черная', 'neut': 'Черное', 'pl': 'Черные'},
        'Голубой': {'masc': 'Голубой', 'fem': 'Голубая', 'neut': 'Голубое', 'pl': 'Голубые'},
        'Темно-синий': {'masc': 'Темно-синий', 'fem': 'Темно-синяя', 'neut': 'Темно-синее', 'pl': 'Темно-синие'},
        'Синий': {'masc': 'Синий', 'fem': 'Синяя', 'neut': 'Синее', 'pl': 'Синие'},
        'Красный': {'masc': 'Красный', 'fem': 'Красная', 'neut': 'Красное', 'pl': 'Красные'},
        'Темно-красный': {'masc': 'Темно-красный', 'fem': 'Темно-красная', 'neut': 'Темно-красное', 'pl': 'Темно-красные'},
        'Зеленый': {'masc': 'Зеленый', 'fem': 'Зеленая', 'neut': 'Зеленое', 'pl': 'Зеленые'},
        'Темно-зеленый': {'masc': 'Темно-зеленый', 'fem': 'Темно-зеленая', 'neut': 'Темно-зеленое', 'pl': 'Темно-зеленые'},
        'Желтый': {'masc': 'Желтый', 'fem': 'Желтая', 'neut': 'Желтое', 'pl': 'Желтые'},
        'Серый': {'masc': 'Серый', 'fem': 'Серая', 'neut': 'Серое', 'pl': 'Серые'},
        'Коричневый': {'masc': 'Коричневый', 'fem': 'Коричневая', 'neut': 'Коричневое', 'pl': 'Коричневые'},
        'Розовый': {'masc': 'Розовый', 'fem': 'Розовая', 'neut': 'Розовое', 'pl': 'Розовые'},
        'Фиолетовый': {'masc': 'Фиолетовый', 'fem': 'Фиолетовая', 'neut': 'Фиолетовое', 'pl': 'Фиолетовые'},
        'Оранжевый': {'masc': 'Оранжевый', 'fem': 'Оранжевая', 'neut': 'Оранжевое', 'pl': 'Оранжевые'},
        'Бежевый': {'masc': 'Бежевый', 'fem': 'Бежевая', 'neut': 'Бежевое', 'pl': 'Бежевые'},
        'Темно-серый': {'masc': 'Темно-серый', 'fem': 'Темно-серая', 'neut': 'Темно-серое', 'pl': 'Темно-серые'},
        'Светло-серый': {'masc': 'Светло-серый', 'fem': 'Светло-серая', 'neut': 'Светло-серое', 'pl': 'Светло-серые'},
    }

    def __init__(self):
        """Инициализация анализатора"""
        self.model = None
        self.processor = None
        self.device = None
        self.is_loaded = False
        self._translation_cache = {}
        self._description_cache = {}
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
        Анализирует изображение одежды и возвращает характеристики на русском языке.
        
        Метод использует три типа генерации описаний:
        1. Общее описание (безусловная генерация)
        2. Детальное описание с фокусом на характеристики одежды
        3. Описание с фокусом на цвет и тип
        
        Все три описания объединяются для более точного парсинга характеристик.
        
        Args:
            image_path: путь к изображению
            
        Returns:
            Словарь с характеристиками одежды на русском языке:
            - clothes_category: категория (jeans, dress, t-shirt и т.д.)
            - clothes_color: цвет на русском (Красный, Синий и т.д.)
            - clothes_material: материал на русском (Деним, Хлопок и т.д.)
            - clothes_brand: бренд (пока пустое поле)
            - clothes_description: подробное описание на русском
            - clothes_name: название вещи на русском
            - clothes_condition: состояние (new, good, excellent, satisfactory)
            
            Возвращает None в случае ошибки
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
            
            # Получаем несколько описаний для большей полноты
            print("Starting BLIP caption generation...")
            
            # 1. Общее описание
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                out_general = self.model.generate(**inputs, max_length=80, num_beams=4)
            caption_general = self.processor.decode(out_general[0], skip_special_tokens=True)
            
            # 2. Детальное описание (цвет, тип, материал, стиль, состояние)
            prompt_detail = "Describe the clothing item in detail: color, type, material, style, condition:"
            inputs_detail = self.processor(image, prompt_detail, return_tensors="pt").to(self.device)
            with torch.no_grad():
                out_detail = self.model.generate(**inputs_detail, max_length=120, num_beams=4)
            caption_detail = self.processor.decode(out_detail[0], skip_special_tokens=True)
            
            # 3. Цвет и тип
            prompt_color = "the clothing color and category:"
            inputs_color = self.processor(image, prompt_color, return_tensors="pt").to(self.device)
            with torch.no_grad():
                out_color = self.model.generate(**inputs_color, max_length=60, num_beams=3)
            caption_color = self.processor.decode(out_color[0], skip_special_tokens=True)
            
            info_logger.info(f"Generated captions: general='{caption_general}', detail='{caption_detail}', color='{caption_color}'")
            print(f"BLIP captions:\n  general: {caption_general}\n  detail: {caption_detail}\n  color: {caption_color}")
            
            combined_caption = f"{caption_general}. {caption_detail}. {caption_color}"
            
            # Парсим описание и извлекаем данные
            parsed_data = self._parse_caption(combined_caption)
            if not parsed_data:
                info_logger.warning("Parsed data is empty - possibly not clothing")
                return None
            
            return parsed_data
            
        except Exception as e:
            er_logger.error(f"Error analyzing image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_caption(self, caption: str) -> Optional[Dict[str, str]]:
        """
        Парсит описание от BLIP и извлекает данные об одежде
        
        Args:
            caption: текстовое описание от модели
            
        Returns:
            Словарь с извлеченными данными или None если одежда не распознана
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
        
        # Определяем категорию (по порядку приоритета)
        category = ''

        def has_word(text: str, word: str) -> bool:
            return re.search(r'\b{}\b'.format(re.escape(word)), text) is not None

        tshirt_markers = ['t-shirt', 't - shirt', 'tshirt', 't shirt', 'tee shirt', 'tee-shirt']
        if any(marker in caption_lower for marker in tshirt_markers) or has_word(caption_lower, 'tee') or has_word(caption_lower, 'top'):
            category = 't-shirt'
        elif has_word(caption_lower, 'shirt') and not any(marker in caption_lower for marker in tshirt_markers):
            category = 'shirt'
        elif has_word(caption_lower, 'blouse'):
            category = 'shirt'
        else:
            # Остальные категории
            for cat, keywords in category_keywords.items():
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
        
        if not category:
            info_logger.warning(f"No clothing category detected in caption: {caption}")
            return None
        
        # Генерируем название вещи с учетом рода
        clothes_name = ''
        meta = self.CATEGORY_METADATA.get(category, {'name': category.title(), 'gender': 'masc'})
        noun = meta['name']
        gender = meta.get('gender', 'masc')
        if color:
            adj = self._adjust_color_form(color, gender)
            clothes_name = f"{adj} {noun.lower()}".strip()
        else:
            clothes_name = noun
        if clothes_name:
            clothes_name = clothes_name[0].upper() + clothes_name[1:]
        
        description_ru = self._build_russian_description(
            caption=caption,
            category=category,
            color=color,
            material=material,
            condition=condition
        )
        
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
    
    def _build_russian_description(
        self,
        caption: str,
        category: str,
        color: str,
        material: str,
        condition: str
    ) -> str:
        """Формирует развернутое описание на русском из распарсенных атрибутов."""
        if caption in self._description_cache:
            return self._description_cache[caption]
        condition_names_ru = {
            'new': 'Как новая',
            'excellent': 'Отличное',
            'good': 'Хорошее',
            'satisfactory': 'Удовлетворительное'
        }
        meta = self.CATEGORY_METADATA.get(category, {'name': 'Предмет одежды', 'gender': 'masc'})
        item_ru = meta['name']
        gender = meta.get('gender', 'masc')
        base_phrase = item_ru
        if color:
            base_phrase = f"{self._adjust_color_form(color, gender)} {item_ru.lower()}"
        base_phrase = base_phrase.strip()
        if base_phrase:
            base_phrase = base_phrase[0].upper() + base_phrase[1:]
        sentences = [f"{base_phrase}."] if base_phrase else []
        if material:
            sentences.append(f"Материал: {material}.")
        else:
            sentences.append("Материал: не определен.")
        condition_ru = condition_names_ru.get(condition, 'Хорошее')
        sentences.append(f"Состояние: {condition_ru}.")
        rough = self._rough_translate_caption(caption, category, color)
        if rough:
            sentences.append(f"Доп. описание: {rough}.")
        description = ' '.join(sentences).strip()
        self._description_cache[caption] = description
        return description
    
    def _rough_translate_caption(self, caption: str, category: str, color: str) -> str:
        """Грубый словарный перевод английского описания на русский (оффлайн)."""
        
        # Проверяем кэш (можно вернуть уже готовое описание)
        if caption in self._translation_cache:
            return self._translation_cache[caption]
        
        result = caption.lower()
        
        # ============================================
        # ЭТАП 0: УДАЛЕНИЕ ПРОМПТОВ И СЛУЖЕБНЫХ ФРАЗ
        # ============================================
        # Удаляем фрагменты промптов, которые попали в описание
        prompt_fragments = [
            'a detailed description of the clothing item, including its',
            'detailed description of the clothing item, including its',
            'a detailed description of',
            'detailed description of',
            'including its',
            'the color and type of clothing in the image:',
            'the color and type of clothing in',
            'color and type of clothing in',
            'in the image:',
            'in the image',
        ]
        
        for fragment in prompt_fragments:
            result = result.replace(fragment, '')
        
        # ============================================
        # ЭТАП 1: СЛОЖНЫЕ ФРАЗЫ И ПОЛНЫЕ ПРЕДЛОЖЕНИЯ
        # ============================================
        # Обрабатываем от самых длинных к самым коротким
        complex_phrases = {
            # Полные предложения с контекстом (женщины в платьях)
            'a woman in a red dress walking down the street': 'Красное платье на женщине, идущей по улице',
            'a woman in a blue dress walking down the street': 'Синее платье на женщине, идущей по улице',
            'a woman in a white dress walking down the street': 'Белое платье на женщине, идущей по улице',
            'a woman in a black dress walking down the street': 'Черное платье на женщине, идущей по улице',
            'a woman in a pink dress walking down the street': 'Розовое платье на женщине, идущей по улице',
            'a woman in a green dress walking down the street': 'Зеленое платье на женщине, идущей по улице',
            
            # Женщины в одежде (носящие)
            'a woman wearing a red dress': 'Женщина в красном платье',
            'a woman wearing a blue dress': 'Женщина в синем платье',
            'a woman wearing a white dress': 'Женщина в белом платье',
            'a woman wearing a black dress': 'Женщина в черном платье',
            'a woman wearing a pink dress': 'Женщина в розовом платье',
            'a woman wearing a white t-shirt': 'Женщина в белой футболке',
            'a woman wearing a black t-shirt': 'Женщина в черной футболке',
            'a woman wearing a blue t-shirt': 'Женщина в синей футболке',
            'a woman wearing a red t-shirt': 'Женщина в красной футболке',
            'a woman wearing a gray t-shirt': 'Женщина в серой футболке',
            'a woman wearing a black shirt': 'Женщина в черной рубашке',
            'a woman wearing a white shirt': 'Женщина в белой рубашке',
            'a woman wearing a blue shirt': 'Женщина в синей рубашке',
            'a woman wearing blue jeans': 'Женщина в синих джинсах',
            'a woman wearing black jeans': 'Женщина в черных джинсах',
            'a woman wearing white jeans': 'Женщина в белых джинсах',
            'a woman wearing black pants': 'Женщина в черных брюках',
            'a woman wearing a black skirt': 'Женщина в черной юбке',
            'a woman wearing a blue skirt': 'Женщина в синей юбке',
            
            # Мужчины в одежде
            'a man wearing a black t-shirt': 'Мужчина в черной футболке',
            'a man wearing a white t-shirt': 'Мужчина в белой футболке',
            'a man wearing a blue t-shirt': 'Мужчина в синей футболке',
            'a man wearing a white shirt': 'Мужчина в белой рубашке',
            'a man wearing a black shirt': 'Мужчина в черной рубашке',
            'a man wearing blue jeans': 'Мужчина в синих джинсах',
            'a man wearing black jeans': 'Мужчина в черных джинсах',
            'a man wearing black pants': 'Мужчина в черных брюках',
            
            # Действия с предлогами
            'walking down the street': 'идет по улице',
            'walking down a street': 'идет по улице',
            'walking on the sidewalk': 'идет по тротуару',
            'walking along the street': 'идет вдоль улицы',
            'standing in front of a wall': 'стоит перед стеной',
            'standing in front of the wall': 'стоит перед стеной',
            'standing on the sidewalk': 'стоит на тротуаре',
            'standing in a room': 'стоит в комнате',
            'standing against a wall': 'стоит у стены',
            'sitting on a bench': 'сидит на скамейке',
            'sitting on the floor': 'сидит на полу',
            'sitting in a chair': 'сидит на стуле',
            'posing for a photo': 'позирует для фото',
            'posing for the camera': 'позирует для камеры',
            'looking at the camera': 'смотрит в камеру',
            'looking away from the camera': 'смотрит в сторону от камеры',
            
            # Описания одежды с деталями (расширенные)
            'with black trim': 'с черной окантовкой',
            'with white trim': 'с белой окантовкой',
            'with red trim': 'с красной окантовкой',
            'with blue trim': 'с синей окантовкой',
            'with gray trim': 'с серой окантовкой',
            'with a black collar': 'с черным воротником',
            'with a white collar': 'с белым воротником',
            'with a blue collar': 'с синим воротником',
            'with long sleeves': 'с длинными рукавами',
            'with short sleeves': 'с короткими рукавами',
            'with no sleeves': 'без рукавов',
            'with pockets': 'с карманами',
            'with buttons': 'с пуговицами',
            'with a zipper': 'с молнией',
            'with a belt': 'с ремнем',
            'and black sleeves': 'и черными рукавами',
            'and white sleeves': 'и белыми рукавами',
            'and blue sleeves': 'и синими рукавами',
            'and red sleeves': 'и красными рукавами',
            'with stripes': 'в полоску',
            'with a pattern': 'с узором',
            'with a print': 'с принтом',
            'with a logo': 'с логотипом',
            'with embroidery': 'с вышивкой',
            'with lace': 'с кружевом',
            'with ruffles': 'с рюшами',
        }
        
        for eng, rus in sorted(complex_phrases.items(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(eng, rus)
        
        # ============================================
        # ЭТАП 2: СРЕДНИЕ ФРАЗЫ (КОМБИНАЦИИ СЛОВ)
        # ============================================
        phrases = {
            # Служебные фразы из промптов
            'clothing item': 'предмет одежды',
            'its color': 'цвет',
            'its type': 'тип',
            'its material': 'материал',
            'its style': 'стиль',
            'its condition': 'состояние',
            
            # Конструкции с глаголами
            'wearing a': 'в',
            'wearing an': 'в',
            'wearing the': 'в',
            'walking down': 'идет по',
            'walking on': 'идет по',
            'walking along': 'идет вдоль',
            'standing in': 'стоит в',
            'standing on': 'стоит на',
            'standing near': 'стоит около',
            'standing by': 'стоит у',
            'standing against': 'стоит у',
            'sitting on': 'сидит на',
            'sitting in': 'сидит в',
            'posing for': 'позирует для',
            'looking at': 'смотрит на',
            
            # Предлоги места
            'in front of': 'перед',
            'next to': 'рядом с',
            'near the': 'около',
            'near a': 'около',
            'behind the': 'позади',
            'behind a': 'позади',
            'inside the': 'внутри',
            'inside a': 'внутри',
            'outside the': 'снаружи',
            'outside a': 'снаружи',
            'against a': 'у',
            'against the': 'у',
            'along the': 'вдоль',
            'along a': 'вдоль',
        }
        
        for eng, rus in phrases.items():
            result = result.replace(eng, rus)
        
        # ============================================
        # ЭТАП 3: АРТИКЛИ (УБИРАЕМ РАНЬШЕ ДРУГИХ СЛОВ)
        # ============================================
        result = result.replace(' a ', ' ')
        result = result.replace(' an ', ' ')
        result = result.replace(' the ', ' ')
        
        # ============================================
        # ЭТАП 4: ОТДЕЛЬНЫЕ СЛОВА (МАКСИМАЛЬНО ПОЛНЫЙ СЛОВАРЬ)
        # ============================================
        words = {
            # ===== СЛУЖЕБНЫЕ СЛОВА ИЗ ПРОМПТОВ =====
            'detailed': 'подробный',
            'description': 'описание',
            'including': 'включая',
            'condition': 'состояние',
            'material': 'материал',
            'type': 'тип',
            'style': 'стиль',
            'front': 'спереди',
            'back': 'сзади',
            'side': 'сбоку',
            
            # ===== ОСНОВНЫЕ ГРАММАТИЧЕСКИЕ ЭЛЕМЕНТЫ =====
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
            ' or ': ' или ',
            ' but ': ' но ',
            ' as ': ' как ',
            
            # ===== ЛЮДИ (С ПРАВИЛЬНЫМИ ОКОНЧАНИЯМИ) =====
            'woman': 'женщина',
            'man': 'мужчина',
            'person': 'человек',
            'people': 'люди',
            'girl': 'девушка',
            'boy': 'парень',
            'lady': 'дама',
            'gentleman': 'джентльмен',
            'child': 'ребенок',
            'children': 'дети',
            'adult': 'взрослый',
            'model': 'модель',
            'male': 'мужской',
            'female': 'женский',
            
            # ===== ДЕЙСТВИЯ (ПРИЧАСТИЯ И ГЛАГОЛЫ) =====
            'walking': 'идущая',
            'standing': 'стоящая',
            'sitting': 'сидящая',
            'wearing': 'носящая',
            'posing': 'позирующая',
            'looking': 'смотрящая',
            'smiling': 'улыбающаяся',
            'holding': 'держащая',
            'carrying': 'несущая',
            'running': 'бегущая',
            'jumping': 'прыгающая',
            'moving': 'движущаяся',
            'dancing': 'танцующая',
            
            # ===== МЕСТА И ОКРУЖЕНИЕ =====
            'street': 'улица',
            'sidewalk': 'тротуар',
            'road': 'дорога',
            'path': 'дорожка',
            'pavement': 'тротуар',
            'room': 'комната',
            'store': 'магазин',
            'shop': 'магазин',
            'mall': 'торговый центр',
            'building': 'здание',
            'house': 'дом',
            'wall': 'стена',
            'floor': 'пол',
            'ground': 'земля',
            'ceiling': 'потолок',
            'background': 'фон',
            'outdoor': 'на улице',
            'outdoors': 'на улице',
            'indoors': 'в помещении',
            'inside': 'внутри',
            'outside': 'снаружи',
            'park': 'парк',
            'garden': 'сад',
            'bench': 'скамейка',
            'chair': 'стул',
            'sofa': 'диван',
            
            # ===== ОДЕЖДА - ЦВЕТ + ПРЕДМЕТ (ПОЛНЫЕ КОМБИНАЦИИ) =====
            # Футболки всех цветов
            'white t-shirt': 'белая футболка',
            'black t-shirt': 'черная футболка',
            'blue t-shirt': 'синяя футболка',
            'red t-shirt': 'красная футболка',
            'gray t-shirt': 'серая футболка',
            'grey t-shirt': 'серая футболка',
            'green t-shirt': 'зеленая футболка',
            'yellow t-shirt': 'желтая футболка',
            'pink t-shirt': 'розовая футболка',
            'purple t-shirt': 'фиолетовая футболка',
            'orange t-shirt': 'оранжевая футболка',
            
            # Рубашки всех цветов
            'white shirt': 'белая рубашка',
            'black shirt': 'черная рубашка',
            'blue shirt': 'синяя рубашка',
            'red shirt': 'красная рубашка',
            'gray shirt': 'серая рубашка',
            'grey shirt': 'серая рубашка',
            'green shirt': 'зеленая рубашка',
            'pink shirt': 'розовая рубашка',
            'purple shirt': 'фиолетовая рубашка',
            
            # Джинсы всех цветов
            'blue jeans': 'синие джинсы',
            'black jeans': 'черные джинсы',
            'white jeans': 'белые джинсы',
            'gray jeans': 'серые джинсы',
            'grey jeans': 'серые джинсы',
            'light blue jeans': 'голубые джинсы',
            'dark blue jeans': 'темно-синие джинсы',
            
            # Платья всех цветов
            'red dress': 'красное платье',
            'blue dress': 'синее платье',
            'white dress': 'белое платье',
            'black dress': 'черное платье',
            'pink dress': 'розовое платье',
            'green dress': 'зеленое платье',
            'yellow dress': 'желтое платье',
            'purple dress': 'фиолетовое платье',
            'orange dress': 'оранжевое платье',
            
            # Брюки всех цветов
            'black pants': 'черные брюки',
            'white pants': 'белые брюки',
            'gray pants': 'серые брюки',
            'grey pants': 'серые брюки',
            'blue pants': 'синие брюки',
            'beige pants': 'бежевые брюки',
            'khaki pants': 'брюки цвета хаки',
            
            # Юбки всех цветов
            'black skirt': 'черная юбка',
            'white skirt': 'белая юбка',
            'red skirt': 'красная юбка',
            'blue skirt': 'синяя юбка',
            'pink skirt': 'розовая юбка',
            'gray skirt': 'серая юбка',
            'grey skirt': 'серая юбка',
            
            # Куртки/пиджаки всех цветов
            'black jacket': 'черная куртка',
            'blue jacket': 'синяя куртка',
            'brown jacket': 'коричневая куртка',
            'gray jacket': 'серая куртка',
            'grey jacket': 'серая куртка',
            'leather jacket': 'кожаная куртка',
            'denim jacket': 'джинсовая куртка',
            'jean jacket': 'джинсовая куртка',
            
            # ===== ОДЕЖДА - ОБЩИЕ ВИДЫ =====
            # Верхняя часть
            't-shirt': 'футболка',
            't - shirt': 'футболка',
            'tshirt': 'футболка',
            'tee shirt': 'футболка',
            'tee': 'футболка',
            'tank top': 'майка',
            'tanktop': 'майка',
            'camisole': 'топ на бретельях',
            'shirt': 'рубашка',
            'blouse': 'блузка',
            'top': 'топ',
            'crop top': 'укороченный топ',
            'tube top': 'топ-бандо',
            'sweater': 'свитер',
            'pullover': 'пуловер',
            'hoodie': 'толстовка с капюшоном',
            'sweatshirt': 'толстовка',
            'cardigan': 'кардиган',
            'blazer': 'пиджак',
            'suit jacket': 'пиджак',
            'vest': 'жилет',
            
            # Нижняя часть
            'jeans': 'джинсы',
            'denim pants': 'джинсы',
            'denim': 'джинсовый',
            'pants': 'брюки',
            'trousers': 'брюки',
            'slacks': 'брюки',
            'shorts': 'шорты',
            'skirt': 'юбка',
            'mini skirt': 'мини-юбка',
            'maxi skirt': 'макси-юбка',
            'midi skirt': 'миди-юбка',
            'leggings': 'леггинсы',
            'tights': 'колготки',
            
            # Платья и комбинезоны
            'dress': 'платье',
            'gown': 'вечернее платье',
            'sundress': 'сарафан',
            'maxi dress': 'длинное платье',
            'mini dress': 'короткое платье',
            'midi dress': 'платье средней длины',
            'jumpsuit': 'комбинезон',
            'romper': 'ромпер',
            'overall': 'комбинезон',
            
            # Верхняя одежда
            'jacket': 'куртка',
            'coat': 'пальто',
            'overcoat': 'пальто',
            'trench coat': 'тренч',
            'raincoat': 'плащ',
            'parka': 'парка',
            'windbreaker': 'ветровка',
            'bomber jacket': 'бомбер',
            
            # Обувь
            'shoes': 'обувь',
            'boots': 'ботинки',
            'ankle boots': 'ботильоны',
            'sneakers': 'кроссовки',
            'trainers': 'кроссовки',
            'sandals': 'сандалии',
            'heels': 'туфли на каблуке',
            'high heels': 'высокие каблуки',
            'flats': 'балетки',
            'loafers': 'лоферы',
            'slippers': 'тапочки',
            
            # Аксессуары
            'scarf': 'шарф',
            'hat': 'шляпа',
            'cap': 'кепка',
            'beanie': 'вязаная шапка',
            'gloves': 'перчатки',
            'tie': 'галстук',
            'bow tie': 'бабочка',
            'belt': 'ремень',
            'bag': 'сумка',
            'purse': 'сумочка',
            'backpack': 'рюкзак',
            'watch': 'часы',
            'glasses': 'очки',
            'sunglasses': 'солнцезащитные очки',
            'jewelry': 'украшения',
            'necklace': 'ожерелье',
            'bracelet': 'браслет',
            'earrings': 'серьги',
            'ring': 'кольцо',
            
            # ===== ЦВЕТА (ПОЛНЫЙ СПЕКТР) =====
            # Оттенки синего
            'light blue': 'голубой',
            'sky blue': 'небесно-голубой',
            'baby blue': 'нежно-голубой',
            'dark blue': 'темно-синий',
            'navy blue': 'темно-синий',
            'navy': 'темно-синий',
            'bright blue': 'ярко-синий',
            'pale blue': 'бледно-голубой',
            'royal blue': 'королевский синий',
            'cobalt blue': 'кобальтово-синий',
            
            # Оттенки красного
            'dark red': 'темно-красный',
            'bright red': 'ярко-красный',
            'light red': 'светло-красный',
            'burgundy': 'бордовый',
            'maroon': 'бордовый',
            'crimson': 'малиновый',
            'scarlet': 'алый',
            'cherry red': 'вишневый',
            
            # Оттенки зеленого
            'dark green': 'темно-зеленый',
            'light green': 'светло-зеленый',
            'olive green': 'оливковый',
            'olive': 'оливковый',
            'lime green': 'салатовый',
            'lime': 'лаймовый',
            'forest green': 'лесной зеленый',
            'mint green': 'мятный',
            'emerald green': 'изумрудный',
            
            # Оттенки серого
            'light gray': 'светло-серый',
            'light grey': 'светло-серый',
            'dark gray': 'темно-серый',
            'dark grey': 'темно-серый',
            'charcoal': 'угольно-серый',
            'slate gray': 'грифельно-серый',
            'silver': 'серебристый',
            
            # Оттенки розового
            'hot pink': 'ярко-розовый',
            'light pink': 'светло-розовый',
            'dark pink': 'темно-розовый',
            'fuchsia': 'фуксия',
            'coral': 'коралловый',
            'salmon': 'лососевый',
            'rose': 'розовый',
            
            # Оттенки коричневого
            'light brown': 'светло-коричневый',
            'dark brown': 'темно-коричневый',
            'chocolate brown': 'шоколадно-коричневый',
            'tan': 'бежевый',
            'camel': 'верблюжий',
            'chestnut': 'каштановый',
            
            # Основные цвета
            'red': 'красный',
            'blue': 'синий',
            'white': 'белый',
            'black': 'черный',
            'green': 'зеленый',
            'yellow': 'желтый',
            'pink': 'розовый',
            'gray': 'серый',
            'grey': 'серый',
            'brown': 'коричневый',
            'purple': 'фиолетовый',
            'violet': 'фиолетовый',
            'lavender': 'лавандовый',
            'lilac': 'сиреневый',
            'orange': 'оранжевый',
            'beige': 'бежевый',
            'cream': 'кремовый',
            'ivory': 'цвета слоновой кости',
            'khaki': 'хаки',
            'turquoise': 'бирюзовый',
            'teal': 'сине-зеленый',
            'cyan': 'голубой',
            'magenta': 'пурпурный',
            'gold': 'золотой',
            'bronze': 'бронзовый',
            'copper': 'медный',
            
            # Специальные цвета
            'multicolored': 'разноцветный',
            'multi-colored': 'разноцветный',
            'colorful': 'яркий',
            'bright': 'яркий',
            'pale': 'бледный',
            'dark': 'темный',
            'light': 'светлый',
            'pastel': 'пастельный',
            'neon': 'неоновый',
            'metallic': 'металлик',
            
            # ===== ДЕТАЛИ И ЭЛЕМЕНТЫ ОДЕЖДЫ =====
            'trimmed': 'с окантовкой',
            'trim': 'окантовка',
            'trims': 'окантовка',
            'collar': 'воротник',
            'collared': 'с воротником',
            'v-neck': 'с V-образным вырезом',
            'crew neck': 'с круглым вырезом',
            'turtleneck': 'с воротником-стойкой',
            'neckline': 'вырез',
            'sleeve': 'рукав',
            'sleeves': 'рукава',
            'long sleeve': 'длинный рукав',
            'short sleeve': 'короткий рукав',
            'sleeveless': 'без рукавов',
            'cap sleeve': 'рукав-крылышко',
            'pocket': 'карман',
            'pockets': 'карманы',
            'button': 'пуговица',
            'buttons': 'пуговицы',
            'buttoned': 'на пуговицах',
            'button-up': 'на пуговицах',
            'button-down': 'на пуговицах',
            'zipper': 'молния',
            'zip': 'молния',
            'zipped': 'на молнии',
            'belt': 'ремень',
            'belted': 'с ремнем',
            'strap': 'лямка',
            'straps': 'лямки',
            'logo': 'логотип',
            'print': 'принт',
            'printed': 'с принтом',
            'graphic': 'с графикой',
            'pattern': 'узор',
            'patterned': 'с узором',
            'embroidered': 'вышитый',
            'embroidery': 'вышивка',
            'lace': 'кружево',
            'lacy': 'кружевной',
            'ruffles': 'рюши',
            'ruffled': 'с рюшами',
            'pleated': 'плиссированный',
            'pleats': 'складки',
            'hem': 'подол',
            'hemline': 'линия подола',
            'seam': 'шов',
            'stitching': 'строчка',
            
            # ===== МАТЕРИАЛЫ =====
            'cotton': 'хлопок',
            'leather': 'кожа',
            'faux leather': 'искусственная кожа',
            'wool': 'шерсть',
            'woolen': 'шерстяной',
            'silk': 'шелк',
            'silky': 'шелковый',
            'satin': 'атлас',
            'velvet': 'бархат',
            'linen': 'лен',
            'polyester': 'полиэстер',
            'synthetic': 'синтетика',
            'knit': 'трикотаж',
            'knitted': 'вязаный',
            'cashmere': 'кашемир',
            'suede': 'замша',
            'canvas': 'холст',
            'mesh': 'сетка',
            'chiffon': 'шифон',
            'tulle': 'тюль',
            'fleece': 'флис',
            'corduroy': 'вельвет',
            'tweed': 'твид',
            
            # ===== СТИЛИ И УЗОРЫ =====
            'striped': 'в полоску',
            'stripy': 'в полоску',
            'checkered': 'в клетку',
            'checked': 'в клетку',
            'plaid': 'в клетку',
            'polka dot': 'в горошек',
            'dotted': 'в горошек',
            'spotted': 'в горошек',
            'floral': 'цветочный',
            'flowered': 'в цветочек',
            'floral print': 'цветочный принт',
            'geometric': 'геометрический',
            'abstract': 'абстрактный',
            'plain': 'однотонный',
            'solid': 'однотонный',
            'solid color': 'однотонный',
            'two-tone': 'двухцветный',
            'tie-dye': 'тай-дай',
            'camouflage': 'камуфляж',
            'camo': 'камуфляж',
            'animal print': 'анималистичный принт',
            'leopard print': 'леопардовый принт',
            'zebra print': 'принт зебры',
            
            # ===== СТИЛИ И ФАСОНЫ =====
            'casual': 'повседневный',
            'formal': 'официальный',
            'business': 'деловой',
            'business casual': 'деловой кэжуал',
            'vintage': 'винтажный',
            'retro': 'ретро',
            'modern': 'современный',
            'contemporary': 'современный',
            'classic': 'классический',
            'traditional': 'традиционный',
            'sporty': 'спортивный',
            'athletic': 'спортивный',
            'elegant': 'элегантный',
            'stylish': 'стильный',
            'fashionable': 'модный',
            'trendy': 'модный',
            'chic': 'шикарный',
            'bohemian': 'богемный',
            'boho': 'бохо',
            'preppy': 'преппи',
            'grunge': 'гранж',
            'punk': 'панк',
            'gothic': 'готический',
            'hipster': 'хипстерский',
            'minimalist': 'минималистичный',
            'romantic': 'романтичный',
            'feminine': 'женственный',
            'masculine': 'мужественный',
            'edgy': 'дерзкий',
            'sophisticated': 'утонченный',
            'glamorous': 'гламурный',
            
            # ===== РАЗМЕР, КРОЙ И ПОСАДКА =====
            'fitted': 'приталенный',
            'tight': 'обтягивающий',
            'loose': 'свободный',
            'baggy': 'мешковатый',
            'oversized': 'оверсайз',
            'relaxed': 'свободный',
            'slim': 'узкий',
            'slim fit': 'приталенный',
            'skinny': 'очень узкий',
            'wide': 'широкий',
            'wide leg': 'с широкими штанинами',
            'straight': 'прямой',
            'straight leg': 'прямые',
            'bootcut': 'с расклешенными штанинами',
            'flared': 'расклешенный',
            'a-line': 'А-силуэт',
            'long': 'длинный',
            'short': 'короткий',
            'cropped': 'укороченный',
            'midi': 'миди',
            'mini': 'мини',
            'maxi': 'макси',
            'knee-length': 'до колена',
            'ankle-length': 'до щиколотки',
            'floor-length': 'в пол',
            'high-waisted': 'с высокой талией',
            'low-rise': 'с заниженной талией',
            'mid-rise': 'со средней посадкой',
            
            # ===== СОСТОЯНИЕ И КАЧЕСТВО =====
            'new': 'новый',
            'brand new': 'совершенно новый',
            'old': 'старый',
            'worn': 'поношенный',
            'used': 'б/у',
            'clean': 'чистый',
            'dirty': 'грязный',
            'stained': 'испачканный',
            'wrinkled': 'мятый',
            'ironed': 'глаженый',
            'torn': 'порванный',
            'ripped': 'порванный',
            'damaged': 'поврежденный',
            'faded': 'выцветший',
            'distressed': 'с эффектом потертости',
            'perfect': 'идеальный',
            'excellent': 'отличный',
            'good': 'хороший',
            'fair': 'удовлетворительный',
            'poor': 'плохой',
            
            # ===== ОПИСАТЕЛЬНЫЕ ПРИЛАГАТЕЛЬНЫЕ =====
            'beautiful': 'красивый',
            'pretty': 'симпатичный',
            'nice': 'приятный',
            'cute': 'милый',
            'lovely': 'прелестный',
            'gorgeous': 'великолепный',
            'stunning': 'потрясающий',
            'attractive': 'привлекательный',
            'simple': 'простой',
            'basic': 'базовый',
            'fancy': 'нарядный',
            'comfortable': 'удобный',
            'cozy': 'уютный',
            'warm': 'теплый',
            'cool': 'прохладный',
            'soft': 'мягкий',
            'smooth': 'гладкий',
            'rough': 'грубый',
            'thick': 'толстый',
            'thin': 'тонкий',
            'lightweight': 'легкий',
            'heavy': 'тяжелый',
            
            # ===== ПОГОДА И СЕЗОН =====
            'summer': 'летний',
            'winter': 'зимний',
            'spring': 'весенний',
            'fall': 'осенний',
            'autumn': 'осенний',
            'seasonal': 'сезонный',
            
            # ===== ФОТО И ПРОЧЕЕ =====
            'photo': 'фото',
            'photograph': 'фотография',
            'picture': 'изображение',
            'image': 'изображение',
            'camera': 'камера',
            'photography': 'фотография',
            'outfit': 'наряд',
            'look': 'образ',
            'ensemble': 'ансамбль',
            'clothing': 'одежда',
            'clothes': 'одежда',
            'apparel': 'одежда',
            'garment': 'предмет одежды',
            'item': 'предмет',
            'piece': 'вещь',
            'style': 'стиль',
            'fashion': 'мода',
            'design': 'дизайн',
            'quality': 'качество',
            'condition': 'состояние',
            'size': 'размер',
            'fit': 'посадка',
            'color': 'цвет',
            'colour': 'цвет',
            'material': 'материал',
            'fabric': 'ткань',
            'texture': 'текстура',
            'detail': 'деталь',
            'details': 'детали',
            'feature': 'особенность',
            'features': 'особенности',
        }
        
        for eng, rus in words.items():
            result = result.replace(eng, rus)
        
        # ============================================
        # ЭТАП 5: ОЧИСТКА И ФОРМАТИРОВАНИЕ
        # ============================================
        # Убираем множественные пробелы
        while '  ' in result:
            result = result.replace('  ', ' ')
        
        # Убираем пробелы перед пунктуацией
        result = result.replace(' ,', ',')
        result = result.replace(' .', '.')
        result = result.replace(' :', ':')
        result = result.replace(' ;', ';')
        result = result.replace(' !', '!')
        result = result.replace(' ?', '?')
        
        # Убираем лишние пробелы в начале и конце
        result = result.strip()
        
        # Первая буква заглавная
        if result:
            result = result[0].upper() + result[1:]
        
        # Если описание получилось слишком коротким или неполным, 
        # создаем более информативное описание на русском
        if len(result) < 15 or not any(char.isalpha() for char in result):
            # Формируем описание из известных данных
            description_parts = []
            
            if color:
                description_parts.append(color)
            
            if category:
                category_names = {
                    'jeans': 'джинсы',
                    'dress': 'платье',
                    'shirt': 'рубашка',
                    't-shirt': 'футболка',
                    'pants': 'брюки',
                    'skirt': 'юбка',
                    'jacket': 'куртка',
                    'shoes': 'обувь',
                }
                if category in category_names:
                    description_parts.append(category_names[category])
            
            if description_parts:
                result = ' '.join(description_parts)
                # Добавляем стандартное начало для полноты
                result = f"Предмет одежды: {result}"
            else:
                result = "Предмет одежды"
        
            self._translation_cache[caption] = result
            return result

    def _adjust_color_form(self, color: str, gender: str) -> str:
        """Возвращает цвет в нужном роде/числе для согласования с предметом."""
        if not color:
            return color
        forms = self.COLOR_FORMS.get(color)
        if forms:
            return forms.get(gender, forms.get('masc', color))
        lower_color = color.lower()
        replacements = {
            'fem': [('ый', 'ая'), ('ой', 'ая'), ('ий', 'яя')],
            'neut': [('ый', 'ое'), ('ой', 'ое'), ('ий', 'ее')],
            'pl': [('ый', 'ые'), ('ой', 'ые'), ('ий', 'ие')]
        }
        for old, new in replacements.get(gender, []):
            if lower_color.endswith(old):
                return color[:-len(old)] + new
        if gender == 'pl' and lower_color.endswith('ыйх'):
            return color[:-3] + 'ых'
        return color


# Глобальный экземпляр анализатора
_analyzer_instance = None


def get_analyzer() -> ClothesVLMAnalyzer:
    """Получить экземпляр анализатора (singleton)"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ClothesVLMAnalyzer()
    return _analyzer_instance
