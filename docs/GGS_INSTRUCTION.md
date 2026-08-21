# Инструкция по генерации журналов ПНР (ГГС / СОДС / Сетевые системы)

Настоящее руководство описывает структуру данных, JSON-схему спецификаций оборудования, процесс генерации Markdown-отчетов и их последующий экспорт в PDF.

---

## 1. Архитектура и принцип работы

Генератор журналов ПНР базируется на модульном пайплайне:
1. **Входные данные**: JSON-спецификации проектов, размещенные в каталоге `equip/<project_code>` или `equip/<project_code>.json`. Дополнительные параметры линий акустики могут загружаться из `equip/<project_code>_loudspeaker_lines.json`.
2. **Контекстный процессор** (`main_md.py`):
   - Загружает и нормализует спецификацию;
   - Автоматически рассчитывает суммарные показатели системы (`central_count`, `modules_count`, `intercoms_count`, `speakers_count`, `power_count`);
   - Подбирает нормативные программы проверок и формирует чек-листы индивидуальных испытаний по каждому типу оборудования;
   - Рассчитывает матрицу акустических измерений (звуковое давление, фоновый шум, превышение $\ge 15\text{ дБА}$, разборчивость 100%);
   - Кодирует графические ассеты (логотип, подписи) и инженерный шрифт в формат Base64 Data URI для автономности документа.
3. **Шаблонизатор Jinja2** (`templates/template_ggs.md`):
   - Генерирует готовый чистовой Markdown-документ со встроенными CSS-стилями и структурой разделов (титул, состав ИТР, основные показатели, общие указания, ведомость оборудования, чек-листы 1–4, протокол ИБП, протокол акустики, акты приемки и автономных испытаний).
4. **Выходные файлы**:
   - `output/Журнал_ПНР_<код_проекта>.md`
   - `output/pdf-fonts.css` (типографические правила и шрифты)
   - Поддержка прямого экспорта в PDF через VS Code (расширение `yzane.markdown-pdf`).

---

## 2. Формальная JSON Schema (Спецификация проекта)

Ниже представлена JSON-схема стандарта **Draft-07**, описывающая структуру входного файла проекта:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GGS_Project_Specification_Schema",
  "description": "Схема структуры входных данных для генератора журнала ПНР систем ГГС и СОДС",
  "type": "object",
  "required": ["document_context", "project", "equipment"],
  "properties": {
    "document_context": {
      "type": "object",
      "description": "Общие реквизиты документа и организации",
      "required": ["org_full", "org_inn_kpp", "system_name_nom", "system_name_rod", "developer_name", "approver_name"],
      "properties": {
        "org_full": { "type": "string", "description": "Полное наименование организации исполнителя ПНР" },
        "org_short": { "type": "string", "description": "Краткое наименование организации" },
        "org_inn_kpp": { "type": "string", "description": "ИНН/КПП организации" },
        "org_address": { "type": "string", "description": "Юридический адрес" },
        "org_phone_email": { "type": "string", "description": "Контакты организации" },
        "approver_title": { "type": "string", "description": "Должность утверждающего лица" },
        "approver_name": { "type": "string", "description": "ФИО утверждающего лица" },
        "developer_title": { "type": "string", "description": "Должность составителя/ответственного лица" },
        "developer_title2": { "type": "string", "description": "Дополнительное подразделение/группа" },
        "developer_name": { "type": "string", "description": "ФИО составителя журнала ПНР" },
        "date_str": { "type": "string", "description": "Дата составления документа (ДД.ММ.ГГГГ)" },
        "system_name_nom": { "type": "string", "description": "Наименование системы в именительном падеже" },
        "system_name_rod": { "type": "string", "description": "Наименование системы в родительном падеже" },
        "category": { "type": "string", "description": "Категория технической сложности системы (например, 'II (вторая)')" },
        "coef_kuf": { "type": "string", "description": "Коэффициент участия в наладке" },
        "coef_kms": { "type": "string", "description": "Коэффициент метрологической сложности" },
        "coef_kinf": { "type": "string", "description": "Коэффициент информативности" },
        "sheet_stage": { "type": "string", "description": "Стадия документации (РД/ПД)" },
        "auto_pass_results": { "type": "boolean", "description": "Автоматическая отметка успешного прохождения тестов" }
      }
    },
    "project": {
      "type": "object",
      "description": "Сведения о строительном объекте и рабочем проекте",
      "required": ["project_code", "project_title", "site_title", "customer", "executor"],
      "properties": {
        "project_code": { "type": "string", "description": "Шифр рабочей документации (например, '12006-81-0600-СС1.2')" },
        "project_title": { "type": "string", "description": "Полное наименование рабочего проекта" },
        "site_title": { "type": "string", "description": "Полное наименование объекта строительства" },
        "site_title_short": { "type": "string", "description": "Краткое наименование объекта" },
        "location_address": { "type": "string", "description": "Географический адрес объекта" },
        "customer": { "type": "string", "description": "Наименование организации Заказчика" },
        "executor": { "type": "string", "description": "Наименование организации Подрядчика (наладочной организации)" },
        "designer": { "type": ["string", "null"], "description": "Генеральный проектировщик" },
        "category": { "type": "string", "description": "Категория сложности" },
        "technical_notes": {
          "type": "object",
          "description": "Технические примечания и особенности построения системы",
          "properties": {
            "central_location": { "type": "string", "description": "Место размещения центрального узла/шкафа" },
            "kspd_cabinet": { "type": "string", "description": "Шкаф интеграции в КСПД" },
            "rasco_connection": { "type": "string", "description": "Точка стыковки с системой оповещения РАСЦО" },
            "power_supply": { "type": "string", "description": "Характеристики системы бесперебойного питания (ИБП)" },
            "related_projects": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Смежные комплекты рабочей документации"
            }
          }
        }
      }
    },
    "equipment": {
      "type": "array",
      "description": "Перечень оборудования, входящего в систему и подлежащего ПНР",
      "items": {
        "type": "object",
        "required": ["equipment_type", "vendor", "name", "model_or_code", "quantity", "work"],
        "properties": {
          "equipment_type": {
            "type": "string",
            "enum": ["switch", "router", "intercom_dis", "intercom_dw", "speaker", "amplifier", "ups", "other"],
            "description": "Тип оборудования для классификации и подбора чек-листа"
          },
          "priority": { "type": "integer", "description": "Порядковый номер / приоритет в ведомости" },
          "vendor": { "type": "string", "description": "Завод-изготовитель или поставщик" },
          "name": { "type": "string", "description": "Наименование и краткая техническая характеристика" },
          "model_or_code": { "type": "string", "description": "Тип, марка, артикул или заказной код" },
          "description": { "type": "string", "description": "Расширенное описание" },
          "quantity": { "type": "integer", "minimum": 1, "description": "Количество единиц оборудования" },
          "port_count": { "type": "integer", "description": "Количество сетевых/абонентских портов" },
          "work": { "type": "string", "description": "Вид наладочных работ и основание" },
          "ferp": {
            "type": "array",
            "description": "Применяемые расценки ФЕРп",
            "items": {
              "type": "object",
              "properties": {
                "code": { "type": "string", "description": "Шифр расценки (например, 'ФЕРп 02-01-002-09')" },
                "title": { "type": "string", "description": "Наименование расценки" }
              }
            }
          },
          "checklist": {
            "type": "object",
            "description": "Индивидуальный чек-лист проверки (если переопределен вручную)",
            "properties": {
              "title": { "type": "string" },
              "norm_doc": { "type": "string" },
              "items": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "num": { "type": "integer" },
                    "step": { "type": "string" },
                    "norm": { "type": "string" },
                    "fact": { "type": "string" },
                    "result": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    },
    "loudspeaker_lines": {
      "type": "array",
      "description": "Спецификация линий громкоговорителей и акустических расчетов (опционально)",
      "items": {
        "type": "object",
        "properties": {
          "line_id": { "type": "string", "description": "Обозначение кабельной линии (например, 'LS6.0.6')" },
          "location": { "type": "string", "description": "Здание, этаж, помещение" },
          "speakers": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "pos": { "type": "string", "description": "Позиция по РД (например, 'LS6.0.6.01')" },
                "model": { "type": "string", "description": "Модель (AR-25, CP-66(T), B-406(T))" },
                "tap_power_w": { "type": "number", "description": "Установленная мощность отвода трансформатора, Вт" },
                "noise_db": { "type": "number", "description": "Фоновый шум, дБА" },
                "signal_db": { "type": "number", "description": "Уровень звукового давления сигнала ГГС, дБА" }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 3. Пример типового JSON-файла проекта

Файл спецификации сохраняется по пути: `equip/<код_проекта>` (или `equip/<код_проекта>.json`):

```json
{
  "document_context": {
    "org_full": "Общество с ограниченной ответственностью «Голд Линк»",
    "org_short": "ООО «Голд Линк»",
    "org_inn_kpp": "7224078140/720301001",
    "org_address": "625016, Россия, Тюменская обл., г. Тюмень, ул. Александра Логунова, д. 11/5",
    "org_phone_email": "info@gold-link.ru",
    "approver_title": "Руководитель технической группы",
    "approver_name": "Грязнов Е.Е.",
    "developer_title": "Главный специалист",
    "developer_title2": "технической группы",
    "developer_name": "Кудря Н.Ю.",
    "date_str": "21.08.2026",
    "system_name_nom": "Система оперативно-диспетчерской связи и громкоговорящей связи (СОДС и ГГС)",
    "system_name_rod": "системы оперативно-диспетчерской связи и громкоговорящей связи (СОДС и ГГС)",
    "category": "II (вторая)",
    "auto_pass_results": true
  },
  "project": {
    "project_code": "12006-81-0600-СС1.2",
    "project_title": "Система оперативно-диспетчерской и громкоговорящей связи. 12006-81-0600-СС1.2",
    "site_title": "Култуминский горно-обогатительный комбинат. Объекты вспомогательных цехов. Площадка обслуживания вспомогательного транспорта",
    "site_title_short": "Култуминский ГОК",
    "location_address": "Забайкальский край, Газимуро-Заводский район",
    "customer": "ООО «Восток-Гео»",
    "executor": "ООО «Голд Линк»",
    "technical_notes": {
      "central_location": "Здание РММ, помещение 105 «Узел связи», шкаф TR6.2.3",
      "kspd_cabinet": "Здание РММ, шкаф TR6.2.2",
      "rasco_connection": "Здание «Главный корпус ОФ», помещение «Серверная», блок П161М РММ-8 БС",
      "power_supply": "Установка питания постоянного тока ШТИЛЬ PS48-0080-2U 2kW/48V с 4 АКБ 40 А·ч (48В)"
    }
  },
  "equipment": [
    {
      "equipment_type": "switch",
      "priority": 1,
      "vendor": "ООО \"Армтел\"",
      "name": "Коммутатор DCN-16U с коммутационным процессорным модулем DCN-Q4E (4хE1) и кабелями",
      "model_or_code": "АРТИКУЛ: 2200200002",
      "quantity": 2,
      "work": "ПНР, настройка, проверка работоспособности и испытания по ФЕРп 02-01-002-09."
    },
    {
      "equipment_type": "router",
      "priority": 2,
      "vendor": "ООО \"Армтел\"",
      "name": "DCN IP-шлюз с тремя модулями E1/SIP",
      "model_or_code": "ARMT.665230.137",
      "quantity": 1,
      "work": "ПНР, настройка, проверка работоспособности и испытания по ФЕРп 02-01-002-09."
    },
    {
      "equipment_type": "intercom_dis",
      "priority": 3,
      "vendor": "ООО \"Армтел\"",
      "name": "Пульт диспетчерской связи DIS на 16 клавиш с микрофоном",
      "model_or_code": "DIS-16",
      "quantity": 4,
      "work": "ПНР, проверка абонентских портов и звукового тракта."
    },
    {
      "equipment_type": "intercom_dw",
      "priority": 4,
      "vendor": "ООО \"Армтел\"",
      "name": "Переговорное устройство всепогодное цифровое DW",
      "model_or_code": "DW-IP-Ex",
      "quantity": 9,
      "work": "ПНР, проверка изоляции, абонентского тракта и встроенного УНЧ."
    },
    {
      "equipment_type": "speaker",
      "priority": 5,
      "vendor": "ООО \"Армтел\"",
      "name": "Громкоговоритель рупорный всепогодный 25 Вт",
      "model_or_code": "AR-25",
      "quantity": 35,
      "work": "Проверка отводов мощности, акустические замеры звукового давления."
    },
    {
      "equipment_type": "ups",
      "priority": 6,
      "vendor": "ГК «Штиль»",
      "name": "Установка электропитания постоянного тока ШТИЛЬ PS48-0080-2U",
      "model_or_code": "PS48-0080-2U 2kW/48V",
      "quantity": 2,
      "work": "Комплексные испытания электропитания и времени автономной работы под нагрузкой."
    }
  ]
}
```

---

## 4. Команды консоли (CLI)

Все операции выполняются через единый скрипт `main_md.py`:

### Генерация журнала ГГС
```bash
py -3 main_md.py render-ggs --project 12006-81-0600-СС1.2
```
*Команда читает спецификацию из `equip/12006-81-0600`, рендерит шаблон `templates/template_ggs.md` и сохраняет готовый Markdown в `output/Журнал_ПНР_12006-81-0600-СС1.2.md`.*

### Универсальная команда генерации (авто-роутинг)
```bash
py -3 main_md.py render --project 12006-81-0600-СС1.2
```
*Если проект отсутствует в сетевой базе коммутаторов, система автоматически находит спецификацию в `equip/` и запускает генератор ГГС.*

### Запуск автоматических тестов
```bash
py -3 -m unittest discover tests
```

---

## 5. Стандарты типографики и оформление

Документ настроен в строгом соответствии с требованиями оформления исполнительной документации:

1. **Иерархия шрифтов**:
   - **Основной текст, списки, пояснения, заключения, примечания**: **14pt** (`line-height: 1.5;`).
   - **Все таблицы** (ведомость оборудования, чек-листы индивидуальных проверок, чек-листы комплексных испытаний 1–4, таблицы СИ, разряд ИБП, таблицы подписей): **12pt**.
   - **Таблица 49 акустических замеров (Приложение Г)**: строго **10pt** (`table.acoustic-table`).
2. **Абзацы и выравнивание**:
   - Выравнивание текста: по ширине (`text-align: justify;`).
   - Отступ первой строки (красная строка): `text-indent: 1.25cm;` (ГОСТ/ЕСКД).
   - Выравнивание в таблицах: первый столбец всегда по левому краю (`table th:first-child, table td:first-child { text-align: left !important; }`).
3. **Шрифт**:
   - Инженерный шрифт **PF Din Text Cond Pro** (подключается через `output/pdf-fonts.css` и Base64 Data URI).

---

## 6. Конвертация в PDF

1. Откройте сгенерированный файл `output/Журнал_ПНР_12006-81-0600-СС1.2.md` в VS Code.
2. Убедитесь, что установлено расширение **Markdown-PDF** (`yzane.markdown-pdf`).
3. Нажмите `F1` (или `Ctrl+Shift+P`), введите команду:
   ```text
   Markdown PDF: Export (pdf)
   ```
4. Итоговый PDF-документ будет сохранен в папке `output/` со всеми встроенными шрифтами, векторным оформлением и подписями.
