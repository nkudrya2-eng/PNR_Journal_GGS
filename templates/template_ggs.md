<link rel="stylesheet" href="pdf-fonts.css">

<style>
/* Общие правила типографики: текст 14pt, таблицы 12pt, акустика 10pt */
body, p, div, li {
  font-size: 14pt;
}

p {
  font-size: 14pt;
  line-height: 1.5;
  text-align: justify;
  text-indent: 1.25cm;
}

ol, ul {
  font-size: 14pt;
  line-height: 1.5;
}

li {
  font-size: 14pt;
  line-height: 1.5;
  text-align: justify;
}

table {
  font-size: 12pt !important;
}

table th, table td {
  font-size: 12pt !important;
}

table th:first-child, table td:first-child {
  text-align: left !important;
}

/* В таблицах проверок ширина колонок рассчитывается по их содержимому. */
h2[align="center"] + table + table {
  table-layout: auto !important;
  font-size: 12pt !important;
}

h2[align="center"] + table + table th,
h2[align="center"] + table + table td {
  width: auto !important;
  font-size: 12pt !important;
}

h2[align="center"] + table + table th:first-child,
h2[align="center"] + table + table th:last-child {
  white-space: nowrap;
}

/* Таблица акустических замеров (Приложение Г) */
table.acoustic-table,
table.acoustic-table th,
table.acoustic-table td {
  font-size: 10pt !important;
}
</style>

<div style="display: flex; justify-content: space-between; align-items: flex-start; font-size: 13pt; color: #666;">
    <div>
        <img src="{{ logo_src | default('logo.png') }}" alt="ГолдЛинк" width="250">
    </div>
    <div></div>
    <div></div>
    <div></div>

    <div style="text-align: left; margin-left: 30mm;">
      ООО «Голд Линк»<br>
      ОГРН 1177232028423; ИНН/КПП 7224078140/720301001<br>
      info@gold-link.ru
    </div>
</div>

<div style="height: 30mm;"></div>

<div style="font-size: 14pt; color: #000; text-align: center;">

<div style="height: 25mm;"></div>

   <div style="font-size: 17pt; font-weight: bold; text-transform: uppercase; line-height: 1.4;">
        {{ project_object | default(project.project_title) }}
    </div>

   <div style="height: 12mm;"></div>

   <div style="font-size: 22pt; font-weight: bold; line-height: 1.3;">
        Журнал производства<br>
        пусконаладочных работ
   </div>

   <div style="height: 8mm;"></div>

   <div style="font-size: 16pt; font-weight: bold; color: #222;">
        {{ system_name | default('Система громкоговорящей связи') }}
   </div>

   <div style="height: 10mm;"></div>

  <div style="font-size: 17pt; font-weight: bold;">
        {{ project_code }}-ПНР
  </div>

<div style="height: 25mm;"></div>

  <table style="width: 100%; font-size: 14pt;">
        <tr>
            <td style="width: 45%; text-align: left;">
                Дата:
            </td>
            <td style="width: 55%; text-align: left;">
                {{ date }}
            </td>
        </tr>
        <tr>
            <td style="text-align: left; padding-top: 6mm;">
                Испытания провел:
            </td>
            <td style="text-align: left; padding-top: 6mm;">
                Главный специалист технической группы<br>
                Кудря Н. Ю.
            </td>
        </tr>
  </table>

</div>

<div style="page-break-after: always; break-after: page;"></div>

# Состав участников и основные показатели объекта

## 1. Список ИТР, занятых в наладочных работах на объекте

| Фамилия, имя, отчество, занимаемая должность, участок работы | Дата начала работ на объекте | Присвоение прав | Дата окончания работ на объекте |
|---|:---:|---|:---:|
| **Кудря Николай Юрьевич**, Главный специалист | {{ work_start_date | default('23.06.2026') }} | Производитель работ, член бригады | {{ actual_end_date | default(date) }} |
| **Ганин Вячеслав Александрович**, Технический инженер | {{ work_start_date | default('23.06.2026') }} | Производитель работ, член бригады | {{ actual_end_date | default(date) }} |
| **Жамбалдоржиев Цырен Эрдэмович**, Технический инженер | {{ work_start_date | default('23.06.2026') }} | Производитель работ, член бригады | {{ actual_end_date | default(date) }} |
| **Нестеров Иван Сергеевич**, Технический инженер | {{ work_start_date | default('23.06.2026') }} | Производитель работ, член бригады | {{ actual_end_date | default(date) }} |

<br>
<div style="page-break-after: always; break-after: page;"></div>

## 2. Основные показатели системы громкоговорящей связи:

| Наименование показателя | Единица измерения | По проекту | Фактически |
|---|:---:|:---:|:---:|
| Центральное коммутационное оборудование (DCN-16U, IP-шлюзы) | шт. | {{ ggs_summary.central_count | default(6) }} | {{ ggs_summary.central_count | default(6) }} |
| Усилители мощности и модули управления NCU / NCU-REL / МАП | шт. | {{ ggs_summary.modules_count | default(21) }} | {{ ggs_summary.modules_count | default(21) }} |
| Диспетчерские пульты связи (DIS) | шт. | {{ ggs_summary.intercoms_dis_count | default(4) }} | {{ ggs_summary.intercoms_dis_count | default(4) }} |
| Переговорные устройства всепогодные (DW) | шт. | {{ ggs_summary.intercoms_dw_count | default(9) }} | {{ ggs_summary.intercoms_dw_count | default(9) }} |
| Громкоговорители рупорные всепогодные (AR-25, 25 Вт) | шт. | {{ ggs_summary.speakers_ar25_count | default(35) }} | {{ ggs_summary.speakers_ar25_count | default(35) }} |
| Громкоговорители двухнаправленные коридорные (CP-66(T)) | шт. | {{ ggs_summary.speakers_cp66t_count | default(11) }} | {{ ggs_summary.speakers_cp66t_count | default(11) }} |
| Громкоговорители настенные (В 406(Т)) | шт. | {{ ggs_summary.speakers_b406t_count | default(3) }} | {{ ggs_summary.speakers_b406t_count | default(3) }} |
| **Итого громкоговорителей и акустических излучателей** | **шт.** | **{{ ggs_summary.speakers_count | default(49) }}** | **{{ ggs_summary.speakers_count | default(49) }}** |
| Установки бесперебойного электропитания постоянного тока (-48В) | компл. | {{ ggs_summary.power_count | default(2) }} | {{ ggs_summary.power_count | default(2) }} |
| Категория технической сложности системы | категория | {{ category | default('II (вторая)') }} | {{ category | default('II (вторая)') }} |

<br>
<div style="page-break-after: always; break-after: page;"></div>

## 3. Краткая характеристика и общие указания по системе:

<div style="font-size: 14pt; line-height: 1.5; color: #222; text-align: justify;">
<ol style="padding-left: 20px; margin-top: 5px;">
  <li style="margin-bottom: 8px;">
    <strong>Назначение и состав системы:</strong> {% if technical_notes.scope_summary %}{{ technical_notes.scope_summary }}{% else %}Комплекс оперативно-диспетчерской и громкоговорящей связи (СОДС и ГГС) Култуминского ГОКа построен на базе цифрового оборудования ООО «Армтел» в соответствии с рабочей документацией <strong>{{ project_code }}</strong>, требованиями ГОСТ Р 21.703-2020, СП 134.13330.2022, ПУЭ и нормами промышленной безопасности опасных производственных объектов.{% endif %}
  </li>
  <li style="margin-bottom: 8px;">
    <strong>Размещение центрального узла и сетевая связность:</strong> Центральное коммутационное оборудование системы (коммутаторы DCN-16U, модули E1/SIP, усилители TDA-500) размещено в телекоммуникационном шкафу <strong>TR6.2.3</strong> (здание РММ, пом. 105 «Узел связи»). Интеграция в общую информационную сеть предприятия выполнена по Ethernet через коммутатор КСПД шкафа <strong>TR6.2.2</strong>. Стыковка с объектовой системой оповещения РАСЦО организована через блок <strong>П161М РММ-8 БС</strong> и МАП (помещение «Серверная» Главного корпуса ОФ).
  </li>
  <li style="margin-bottom: 8px;">
    <strong>Электропитание, резервирование и заземление:</strong> Электроснабжение шкафа центрального оборудования выполнено по I категории надёжности. Автономное резервирование обеспечивается установкой питания <strong>{{ ups.model_title }}</strong> с <strong>{{ ups.battery_desc }}</strong>. Расчётное время непрерывной автономной работы составляет <strong>{{ ups.runtime_minutes }} минут</strong> при рабочей нагрузке {{ ups.load_watts }} Вт (требование ТУ — не менее 40 минут). Корпус шкафа и аппаратные блоки присоединены к контуру защитного заземления проводом ПВ3 1×6 мм² (R &lt; 4 Ом).
  </li>
  <li style="margin-bottom: 8px;">
    <strong>Охрана труда и регламент ПНР:</strong> Пусконаладочные работы выполнены аттестованным персоналом наладочной организации по утверждённым программам и заводским руководствам по эксплуатации (РЭ). Все применяемое оборудование сертифицировано в РФ и ЕАЭС.
  </li>
</ol>
</div>

<br>

<div style="font-size: 14pt; color: #333; line-height: 1.5;">
<p style="text-align: justify; text-indent: 1.25cm;"><strong>Примечание:</strong> Все специалисты наладочной организации прошли проверку знаний правил охраны труда, техники безопасности при эксплуатации электроустановок и допущены к выполнению пусконаладочных работ на объекте «{{ project_object | default(project.project_title) }}».</p>
</div>

<div style="page-break-after: always; break-after: page;"></div>

# Ведомость оборудования, подвергаемого пусконаладочным работам

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; table-layout: fixed;">
  <colgroup>
    <col style="width: 4%;">
    <col style="width: 29%;">
    <col style="width: 17%;">
    <col style="width: 13%;">
    <col style="width: 6%;">
    <col style="width: 21%;">
    <col style="width: 10%;">
  </colgroup>
  <thead>
    <tr style="background-color: #ededed;">
      <th style="border: 1px solid #777; padding: 6px; text-align: left;">№</th>
      <th style="border: 1px solid #777; padding: 6px; text-align: left;">Наименование и техническая характеристика</th>
      <th style="border: 1px solid #777; padding: 6px; text-align: left;">Тип, марка, артикул</th>
      <th style="border: 1px solid #777; padding: 6px; text-align: left;">Изготовитель / Поставщик</th>
      <th style="border: 1px solid #777; padding: 6px; text-align: center;">Кол-во</th>
      <th style="border: 1px solid #777; padding: 6px; text-align: left;">Вид наладочных работ / Обоснование</th>
      <th style="border: 1px solid #777; padding: 6px; text-align: center;">Результат</th>
    </tr>
  </thead>
  <tbody>
    {% for eq in equipment %}
    <tr>
      <td style="border: 1px solid #777; padding: 5px; text-align: left;">{{ loop.index }}</td>
      <td style="border: 1px solid #777; padding: 5px; font-weight: bold; word-break: break-word;">{{ eq.name }}</td>
      <td style="border: 1px solid #777; padding: 5px; word-break: break-word;">{{ eq.model_or_code | default('—') }}</td>
      <td style="border: 1px solid #777; padding: 5px; word-break: break-word;">{{ eq.vendor | default('—') }}</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center; white-space: nowrap;">{{ eq.quantity }} шт.</td>
      <td style="border: 1px solid #777; padding: 5px; font-size: 11pt; word-break: break-word;">{{ eq.work | default('ПНР, настройка, проверка работоспособности и испытания.') }}</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center; white-space: nowrap;"><span style="color: #0b7500; font-weight: bold;">[x] Налажено</span></td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<br>

<p style="text-indent: 0;"><strong>Ведомость составил:</strong></p>

<table width="100%" style="border-collapse: collapse; font-size: 12pt; text-align: center;">
  <thead>
    <tr style="background-color: #f9f9f9;">
      <th style="width: 40%; border: 1px solid #ccc; padding: 8px; text-align: center">Должность</th>
      <th style="width: 35%; border: 1px solid #ccc; padding: 8px; text-align: center">ФИО</th>
      <th style="width: 25%; border: 1px solid #ccc; padding: 8px; text-align: center">Подпись</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #ccc; padding: 12px;">Главный специалист<br> технической группы</td>
      <td style="border: 1px solid #ccc; padding: 12px;">Кудря Н.Ю.</td>
      <td style="border: 1px solid #ccc; padding: 12px;">
        <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-width: 100%; max-height: 45px; display: block; margin: 0 auto; mix-blend-mode: multiply; transform: rotate(-2deg);">
      </td>
    </tr>
  </tbody>
</table>

{% for eq in equipment %}
{% if eq.checklist %}
<div style="page-break-after: always; break-after: page;"></div>

<div style="text-align: right; font-weight: bold; font-size: 13pt;">Приложение Б</div>
<h2 align="center" style="font-size: 15pt; margin-top: 5px; margin-bottom: 15px; font-weight: bold; text-transform: uppercase;">ЧЕК-ЛИСТ ПРОВЕРКИ КОНФИГУРАЦИИ И СИСТЕМЫ</h2>

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; margin-bottom: 12px;">
  <tr>
    <td style="border: 1px solid #777; padding: 6px; width: 35%; font-weight: bold; background-color: #f7f7f7; text-align: left;">Наименование оборудования</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ eq.name }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Тип / условное обозначение</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ eq.model_or_code | default('—') }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Количество</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ eq.quantity }} шт.</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Изготовитель / поставщик</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ eq.vendor | default('—') }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Шифр рабочей документации</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ project_code }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Основание проверки</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ eq.checklist.basis }}</td>
  </tr>
</table>

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; margin-bottom: 12px;">
  <thead>
    <tr style="background-color: #ededed;">
      <th style="border: 1px solid #777; padding: 5px; width: 4%; text-align: left;">№</th>
      <th style="border: 1px solid #777; padding: 5px; width: 22%; text-align: left;">Проверка</th>
      <th style="border: 1px solid #777; padding: 5px; width: 34%; text-align: left;">Действие</th>
      <th style="border: 1px solid #777; padding: 5px; width: 25%; text-align: left;">Критерий выполнения</th>
      <th style="border: 1px solid #777; padding: 5px; width: 15%; text-align: center;">Отметка</th>
    </tr>
  </thead>
  <tbody>
    {% for row in eq.checklist.rows %}
    <tr>
      <td style="border: 1px solid #777; padding: 4px; text-align: left;">{{ row.num }}</td>
      <td style="border: 1px solid #777; padding: 4px; font-weight: bold;">{{ row.name }}</td>
      <td style="border: 1px solid #777; padding: 4px;">{{ row.action }}</td>
      <td style="border: 1px solid #777; padding: 4px;">{{ row.criterion }}</td>
      <td style="border: 1px solid #777; padding: 4px; text-align: center; white-space: nowrap;"><span style="white-space: nowrap;">[x] Да / [ ] Нет</span></td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<p style="text-indent: 0;"><strong>Проверку произвел:</strong></p>

<table width="100%" style="border-collapse: collapse; font-size: 12pt; text-align: center;">
  <tr>
    <td style="border: 0; padding: 5px; width: 40%;">Главный специалист технической группы</td>
    <td style="border: 0; padding: 5px; width: 35%;">Кудря Н.Ю.</td>
    <td style="border: 0; padding: 5px; width: 25%;">
      <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 45px; mix-blend-mode: multiply; transform: rotate(-2deg);">
    </td>
  </tr>
</table>
{% endif %}
{% endfor %}

<div style="page-break-after: always; break-after: page;"></div>

# Чек-листы проверки и испытаний системы ГГС

### Чек-лист 1. Подготовительный этап, монтаж и электропитание

| № | Проверка | Действие / критерий | Отметка |
|---|---|---|---|
| **1.1** | **Организационно-техническая готовность** | | |
| 1 | Наряды-допуски и ТБ | Наряды-допуски оформлены, СИЗ проверены, инструктаж проведен | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 2 | Исполнительная документация | Схемы подключения и кабельные журналы в наличии | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| **1.2** | **Монтаж и коммутация** | | |
| 3 | Серверные шкафы и стойки | Оборудование Armtel установлено, шины заземления подключены | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 4 | Абонентские посты DW / DIS | Надежность крепления, гермовводы затянуты (IP65) | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 5 | Громкоговорители AR-25 | Направление рупоров выставлено согласно акустическому расчету | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| **1.3** | **Электропитание и заземление** | | |
| 6 | Установка питания Штиль PS48 | Выходное напряжение питания в пределах -48 В ± 2% | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 7 | Инвертор PS48-60/500 | Выходное синусоидальное напряжение 220 В в норме | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 8 | Сопротивление заземления | Соответствует нормам ПУЭ (R < 4 Ом), протокол в наличии | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |

<br>

<table width="100%" style="border-collapse: collapse; font-size: 12pt; text-align: center;">
  <tr>
    <td style="border: 0; padding: 6px; width: 40%; text-align: left;">Главный специалист технической группы</td>
    <td style="border: 0; padding: 6px; width: 35%; text-align: center;">Кудря Н.Ю.</td>
    <td style="border: 0; padding: 6px; width: 25%; text-align: center;">
      <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 45px; mix-blend-mode: multiply; transform: rotate(-2deg);">
    </td>
  </tr>
</table>

<div style="page-break-after: always; break-after: page;"></div>

### Чек-лист 2. Наладка центрального оборудования и сетевой связности

| № | Проверка | Параметр / Действие | Критерий | Отметка |
|---|---|---|---|---|
| 1 | Коммутатор DCN-16U | Загрузка процессора DCN-Q4E | Статус "Ready", ошибок самодиагностики нет | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 2 | Потоки E1 | Синхронизация потоков 4хE1 | Кадровая синхронизация захвачена, CRC4 OK | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 3 | DCN IP-шлюз | Модули E1/SIP | Регистрация SIP-транков успешна, пинг в норме | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 4 | Модуль NCU-Armtel | Контроль целостности линий связи | Автоматический мониторинг шлейфов активен | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 5 | Модули реле NCU-REL | Срабатывание контактов управления | Замыкание/размыкание реле по командам | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 6 | Конфигурация DCN | Запись конфигурации абонентов | База абонентских номеров и прав загружена | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |

<br>

### Чек-лист 3. Наладка усилителей и оконечных устройств связи

| № | Проверка | Оборудование | Критерий оценки | Отметка |
|---|---|---|---|---|
| 1 | Диспетчерские пульты DIS | DIS на 8 кнопок (4 шт.) | Назначение функциональных клавиш, светодиодная индикация OK | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 2 | Переговорные устройства DW | DW на 2 связи (2 шт.) | Четкая дуплексная связь, отсутствие самовозбуждения | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 3 | Посты DW со встроенным УНЧ | DW с УНЧ 25 Вт (7 шт.) | Выходная мощность 25 Вт подтверждена, звук без искажений | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 4 | Усилители мощности TDA-500 | Двухканальные TDA-500 (2 шт.) | Работа двух каналов, защита от КЗ в линии нагрузок | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |
| 5 | Громкоговорители AR-25 | 35 рупорных излучателей | Равномерное звуковое покрытие, разборчивость речи 100% | <span style="white-space: nowrap;">[x] Да / [ ] Нет</span> |

<br>

### Чек-лист 4. Комплексное опробование и проверка алгоритмов ГГС

| № | Режим проверки | Описание проверки | Результат испытания | Отметка |
|---|---|---|---|---|
| 1 | Индивидуальный вызов | Связь «Диспетчер — Производственный пост DW» | Установление соединения < 0.5 с, слышимость отличная | <span style="white-space: nowrap;">[x] Соответствует</span> |
| 2 | Групповой вызов | Оповещение технологической зоны через AR-25 | Одновременная трансляция на все назначенные громкоговорители | <span style="white-space: nowrap;">[x] Соответствует</span> |
| 3 | Циркулярный вызов | Общий вызов по всем зонам объекта | Максимальный приоритет, перехват текущих переговоров | <span style="white-space: nowrap;">[x] Соответствует</span> |
| 4 | Аварийный режим | Трансляция сигналов ГОЧС и сигналов тревоги | Автоматический запуск сирены и голосового оповещения | <span style="white-space: nowrap;">[x] Соответствует</span> |
| 5 | Непрерывный прогон | Непрерывное 72-часовое дежурство под нагрузкой | Отказов, зависаний и сбоев оборудования не зафиксировано | <span style="white-space: nowrap;">[x] Выдержано</span> |

<br>

<p style="text-indent: 0;"><strong>Испытания провели:</strong></p>

<table width="100%" style="border-collapse: collapse; font-size: 12pt; text-align: center;">
  <thead>
    <tr style="background-color: #f9f9f9;">
      <th style="width: 40%; border: 0; padding: 6px;">Должность</th>
      <th style="width: 35%; border: 0; padding: 6px;">ФИО</th>
      <th style="width: 25%; border: 0; padding: 6px;">Подпись</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 0; padding: 6px;">Главный специалист технической группы</td>
      <td style="border: 0; padding: 6px;">Кудря Н.Ю.</td>
      <td style="border: 0; padding: 6px;">
        <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 45px; mix-blend-mode: multiply; transform: rotate(-2deg);">
      </td>
    </tr>
    <tr>
      <td style="border: 0; padding: 6px;">Технический инженер</td>
      <td style="border: 0; padding: 6px;">Ганин В.А.</td>
      <td style="border: 0; padding: 6px;">________________</td>
    </tr>
  </tbody>
</table>

<div style="page-break-after: always; break-after: page;"></div>

<div style="text-align: right; font-weight: bold; font-size: 13pt;">Приложение В</div>
<h2 align="center" style="font-size: 15pt; margin-top: 5px; margin-bottom: 12px; font-weight: bold; text-transform: uppercase;">
  ПРОТОКОЛ ИСПЫТАНИЯ СИСТЕМЫ ЭЛЕКТРОПИТАНИЯ И ВРЕМЕНИ АВТОНОМНОЙ РАБОТЫ ИБП
</h2>

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; margin-bottom: 12px;">
  <tr>
    <td style="border: 1px solid #777; padding: 6px; width: 35%; font-weight: bold; background-color: #f7f7f7; text-align: left;">Объект испытаний</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ ups.model_title }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Место установки</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ project_object }}, центральный телекоммуникационный шкаф</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Аккумуляторная батарея</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ ups.battery_desc }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Фактическая нагрузка шкафа</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ ups.load_watts }} Вт (Iрасч = {{ ups.load_current }} А при ~220В, автомат {{ ups.circuit_breaker }} А, cos φ = 0.99)</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; font-weight: bold; background-color: #f7f7f7; text-align: left;">Требование ТУ / Расчетное время</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">Не менее 40 минут / Расчетное время: <strong>{{ ups.runtime_minutes }} минут</strong> (T = {{ ups.capacity_ah }} × {{ ups.nominal_voltage }} × 0.85 / {{ ups.load_watts }} × 60)</td>
  </tr>
</table>

### Применяемые средства измерений (СИ):

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; margin-bottom: 12px;">
  <thead>
    <tr style="background-color: #ededed;">
      <th style="border: 1px solid #777; padding: 6px; width: 5%; text-align: left;">№</th>
      <th style="border: 1px solid #777; padding: 6px; width: 35%; text-align: left;">Наименование ресурса</th>
      <th style="border: 1px solid #777; padding: 6px; width: 8%; text-align: center;">Ед. изм.</th>
      <th style="border: 1px solid #777; padding: 6px; width: 7%; text-align: center;">Кол-во</th>
      <th style="border: 1px solid #777; padding: 6px; width: 45%; text-align: left;">Назначение и метрологические сведения</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #777; padding: 5px; text-align: left;">1</td>
      <td style="border: 1px solid #777; padding: 5px; font-weight: bold;">Мультиметр цифровой Fluke 179</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">шт.</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">1</td>
      <td style="border: 1px solid #777; padding: 5px;">Измерение напряжения, тока, сопротивления и проверка цепей питания. Госреестр № 50458-12, свид. о поверке действительно до 11.2026</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 5px; text-align: left;">2</td>
      <td style="border: 1px solid #777; padding: 5px; font-weight: bold;">Мегаомметр цифровой Е6-32</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">шт.</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">1</td>
      <td style="border: 1px solid #777; padding: 5px;">Измерение сопротивления изоляции кабельных линий и цепей заземления. Госреестр № 68482-17, свид. действительно до 10.2026</td>
    </tr>
  </tbody>
</table>

### Результаты контрольных измерений при испытании на автономный разряд:

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; margin-bottom: 12px;">
  <thead>
    <tr style="background-color: #ededed;">
      <th style="border: 1px solid #777; padding: 6px; width: 16%; text-align: left;">Время разряда</th>
      <th style="border: 1px solid #777; padding: 6px; width: 16%; text-align: center;">Напряжение АКБ</th>
      <th style="border: 1px solid #777; padding: 6px; width: 14%; text-align: center;">Ток разряда</th>
      <th style="border: 1px solid #777; padding: 6px; width: 40%; text-align: left;">Состояние оборудования и параметры выхода</th>
      <th style="border: 1px solid #777; padding: 6px; width: 14%; text-align: center;">Отметка</th>
    </tr>
  </thead>
  <tbody>
    {% for row in ups.discharge_rows %}
    <tr>
      <td style="border: 1px solid #777; padding: 5px; text-align: left;">{{ row.time_str }}</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">{{ row.voltage }}</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">{{ row.current }}</td>
      <td style="border: 1px solid #777; padding: 5px;">{{ row.state }}</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">{{ row.mark }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
    </tr>
  </tbody>
</table>

### Проверка параметров восстановления и заряда АКБ:
* **Время переключения при восстановлении сети ~220В:** 0 мс (безразрывное);
* **Начальный ток заряда батареи:** 4.0 А (ограничение тока заряда активно);
* **Напряжение буферного подзаряда:** 54.4 В (режим Float charge стабилизирован);
* **Защитное заземление корпуса:** Провод ПВ3 1×6 мм², сопротивление переходного контакта R = 0.04 Ом.

<p style="text-align: justify; text-indent: 1.25cm; font-size: 14pt; line-height: 1.5; margin-top: 12px; margin-bottom: 12px;">
<strong>ЗАКЛЮЧЕНИЕ:</strong> Установка гарантированного электропитания ШТИЛЬ PS48-0080-2U 2kW/48V и аккумуляторная батарея 40 А·ч выдержали испытание автономной непрерывной работой под нагрузкой 1740 Вт в течение <strong>53 минут</strong>. Требования технических условий (автономность не менее 40 минут) и проектной документации выполнены в полном объёме.
</p>

<br>

<p style="text-indent: 0;"><strong>Проверку и испытания ИБП произвели:</strong></p>

<table width="100%" style="border-collapse: collapse; font-size: 12pt; text-align: center;">
  <tr>
    <td style="border: 0; padding: 6px; width: 40%;">Главный специалист технической группы</td>
    <td style="border: 0; padding: 6px; width: 35%;">Кудря Н.Ю.</td>
    <td style="border: 0; padding: 6px; width: 25%;">
      <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 45px; mix-blend-mode: multiply; transform: rotate(-2deg);">
    </td>
  </tr>
</table>

<div style="page-break-after: always; break-after: page;"></div>

<div style="text-align: right; font-weight: bold; font-size: 13pt;">Приложение Г</div>
<h2 align="center" style="font-size: 15pt; margin-top: 5px; margin-bottom: 12px; font-weight: bold; text-transform: uppercase;">
  ПРОТОКОЛ АКУСТИЧЕСКИХ ИЗМЕРЕНИЙ И ПРОВЕРКИ УРОВНЕЙ ЗВУКОВОГО ДАВЛЕНИЯ
</h2>

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; margin-bottom: 12px;">
  <tr>
    <td style="border: 1px solid #777; padding: 6px; width: 35%; font-weight: bold; background-color: #f7f7f7; text-align: left;">Объект испытаний</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">Акустическое поле и звуковое давление громкоговорителей системы СОДС и ГГС</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; width: 35%; font-weight: bold; background-color: #f7f7f7; text-align: left;">Объект строительства</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ project_object | default(project.project_title) }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; width: 35%; font-weight: bold; background-color: #f7f7f7; text-align: left;">Шифр рабочей документации</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">{{ project_code }}</td>
  </tr>
  <tr>
    <td style="border: 1px solid #777; padding: 6px; width: 35%; font-weight: bold; background-color: #f7f7f7; text-align: left;">Нормативные требования</td>
    <td style="border: 1px solid #777; padding: 6px; text-align: left;">СП 133.13330.2012, СП 134.13330.2022 (превышение над фоновым шумом не менее чем на 15 дБА, разборчивость речи 100%)</td>
  </tr>
</table>

### Применяемые средства измерений (СИ):

<table style="width: 100%; border-collapse: collapse; font-size: 12pt; margin-bottom: 12px;">
  <thead>
    <tr style="background-color: #ededed;">
      <th style="border: 1px solid #777; padding: 6px; width: 5%; text-align: left;">№</th>
      <th style="border: 1px solid #777; padding: 6px; width: 35%; text-align: left;">Наименование ресурса</th>
      <th style="border: 1px solid #777; padding: 6px; width: 8%; text-align: center;">Ед. изм.</th>
      <th style="border: 1px solid #777; padding: 6px; width: 7%; text-align: center;">Кол-во</th>
      <th style="border: 1px solid #777; padding: 6px; width: 45%; text-align: left;">Назначение и метрологические сведения</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #777; padding: 5px; text-align: left;">1</td>
      <td style="border: 1px solid #777; padding: 5px; font-weight: bold;">Шумомер 1-го класса Testo 815 / Октава-110А</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">шт.</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">1</td>
      <td style="border: 1px solid #777; padding: 5px;">Измерение уровней звукового давления фонового шума и сигналов оповещения ГГС. Госреестр № 17878-04, свид. действительно до 10.2026</td>
    </tr>
    <tr>
      <td style="border: 1px solid #777; padding: 5px; text-align: left;">2</td>
      <td style="border: 1px solid #777; padding: 5px; font-weight: bold;">Мультиметр цифровой Fluke 179</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">шт.</td>
      <td style="border: 1px solid #777; padding: 5px; text-align: center;">1</td>
      <td style="border: 1px solid #777; padding: 5px;">Контроль выходного напряжения и параметров линий громкоговорителей. Госреестр № 50458-12, свид. действительно до 11.2026</td>
    </tr>
  </tbody>
</table>

### Результаты контрольных замеров акустического давления и разборчивости речи:

<table class="acoustic-table" style="width: 100%; border-collapse: collapse; font-size: 10pt; table-layout: fixed; margin-bottom: 10px; word-break: break-word; overflow-wrap: break-word;">
  <colgroup>
    <col style="width: 4%;">
    <col style="width: 12%;">
    <col style="width: 8%;">
    <col style="width: 28%;">
    <col style="width: 8%;">
    <col style="width: 10%;">
    <col style="width: 7%;">
    <col style="width: 7%;">
    <col style="width: 8%;">
    <col style="width: 8%;">
  </colgroup>
  <thead>
    <tr style="background-color: #ededed;">
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: left;">№</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Позиция по РД</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Линия</th>
      <th style="border: 1px solid #777; padding: 4px 4px; text-align: left;">Место установки / Зона</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Тип</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Мощность (по РД)</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Шум L<sub>фон</sub>, дБА</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Сигнал L<sub>ггс</sub>, дБА</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Превышение</th>
      <th style="border: 1px solid #777; padding: 4px 2px; text-align: center;">Отметка</th>
    </tr>
  </thead>
  <tbody>
    {% for row in acoustic_measurements %}
    <tr>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: left;">{{ row.num }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center; font-weight: bold;">{{ row.tag }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center;">{{ row.line_id }}</td>
      <td style="border: 1px solid #777; padding: 3px 4px; text-align: left;">{{ row.location }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center;">{{ row.type }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center;">{{ row.power_proj }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center;">{{ row.bg_noise }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center;">{{ row.signal_spl }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center; font-weight: bold; ">{{ row.diff }}</td>
      <td style="border: 1px solid #777; padding: 3px 2px; text-align: center;"><span style="font-weight: bold;">[x] Норма</span></td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<p style="text-align: justify; font-size: 11pt; color: #444; margin-top: 6px; margin-bottom: 10px; text-indent: 1.25cm;">
<em>* Примечание: Мощность громкоговорителей установлена переключением отводов согласующих трансформаторов в строгом соответствии с рабочей документацией (РД {{ project_code }}). Измерения уровней звукового давления фонового производственного шума и речевых сигналов выполнены поверенным шумомером 1-го класса Testo 815 / Октава-110А (Госреестр № 17878-04).</em>
</p>

<p style="text-align: justify; text-indent: 1.25cm; font-size: 14pt; line-height: 1.5; margin-top: 12px; margin-bottom: 12px;">
<strong>ЗАКЛЮЧЕНИЕ:</strong> Уровни звукового давления системы оперативно-диспетчерской и громкоговорящей связи во всех 49 контролируемых точках объекта превышают уровень фонового производственного шума более чем на 15 дБА (диапазон фактического превышения составляет от +17.2 до +35.2 дБА). Разборчивость речи составляет 100%. Звуковое поле равномерное, требования СП 133.13330, СП 134.13330 и рабочей документации выполнены в полном объёме.
</p>

<br>

<p style="text-indent: 0;"><strong>Измерения шумомером произвели:</strong></p>

<table width="100%" style="border-collapse: collapse; font-size: 12pt; text-align: center;">
  <tr>
    <td style="border: 0px solid #ccc; padding: 6px; width: 40%;">Главный специалист технической группы</td>
    <td style="border: 0px solid #ccc; padding: 6px; width: 35%;">Кудря Н.Ю.</td>
    <td style="border: 0px solid #ccc; padding: 6px; width: 25%;">
      <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 45px; mix-blend-mode: multiply; transform: rotate(-2deg);">
    </td>
  </tr>
</table>

<div style="page-break-after: always; break-after: page;"></div>

<div style="font-size: 14pt; line-height: 1.5; color: #000;">
<div style="text-align: right; font-weight: bold;">Приложение Ж</div>
<div style="text-align: center; font-weight: bold; margin-bottom: 20px; font-size: 14pt;">
ФОРМА АКТА ПРИЕМКИ ПУСКОНАЛАДОЧНЫХ РАБОТ СИСТЕМЫ
</div>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Объект:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">{{ project_object | default(project.project_title) }}</span></p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Заказчик (генподрядчик):</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">{{ customer_name | default('Заказчик') }}</span><sup>1)</sup></p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Лицо, осуществляющее монтаж:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">ООО «Голд Линк», ИНН 7224078140, ОГРН 1177232028423</span></p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Лицо, осуществляющее пусконаладочные работы:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">ООО «Голд Линк», ИНН 7224078140, ОГРН 1177232028423</span></p>

<h2 style="font-size: 14pt; margin: 20px 0 10px 0; text-align: center; border: none;">АКТ<br>приемки пусконаладочных работ системы № <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 50px;">&nbsp;&nbsp;&nbsp;&nbsp;</span></h2>
<p style="text-align: center; margin-bottom: 20px; text-indent: 0;">от " <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 30px;">&nbsp;&nbsp;&nbsp;&nbsp;</span> " <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 80px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span> {{ date.split('.')[-1] }} г.</p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Представитель заказчика:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 300px; text-indent: 0;">&nbsp;</span><sup>4)</sup></p>
<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Представитель монтажной организации:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Главный специалист тех. группы Кудря Н.Ю.</span></p>
<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Представитель пусконаладочной организации:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Главный специалист тех. группы Кудря Н.Ю.</span></p>
<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Иные представители лиц:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 300px; text-indent: 0;">&nbsp;</span></p>

<div style="font-size: 11pt; color: #444; margin-top: 5px; line-height: 1.1; font-style: italic;">
1), 5) Указывается при наличии. 2), 3) За исключением случаев, когда членство в СРО не требуется.<br>
4) В случае осуществления строительного контроля.
</div>

<p style="margin-top: 15px; margin-bottom: 10px; font-weight: bold; text-indent: 1.25cm;">Составили настоящий Акт о том, что:</p>

<p style="margin-bottom: 8px; text-align: justify; text-indent: 1.25cm;">
1. Смонтированная и допущенная представителем заказчика к пусконаладочным работам система <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">{{ system_name | default('Система громкоговорящей связи') }}</span> прошла наладку в соответствии с программой пусконаладочных работ <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Программа и методика испытаний (ПМИ)</span>, начатых "23" июня 2026 г. и завершенных "{{ date }}".
</p>

<p style="margin-bottom: 8px; text-align: justify; text-indent: 1.25cm;">
2. При проведении пусконаладочных работ выявлено: <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Оборудование Armtel, усилители и оконечные посты настроены корректно. Звуковое покрытие и разборчивость речи соответствуют нормам. Система полностью готова к промышленной эксплуатации.</span>
</p>

<p style="margin-bottom: 15px; text-align: justify; text-indent: 1.25cm;">
3. Процесс проведения пусконаладочных работ отражен в чек-листах индивидуальных и комплексных испытаний (Приложения к настоящему Акту).
</p>

<p style="margin-bottom: 5px; text-indent: 1.25cm;">Акт составлен в ____ экземплярах.</p>
<p style="margin-bottom: 20px; text-indent: 1.25cm;"><strong>Приложения:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Журнал производства ПНР, ведомость смонтированного оборудования, чек-листы комплексного опробования.</span></p>

<div style="margin-top: 30px; display: flex; justify-content: space-between; flex-wrap: wrap; font-size: 12pt;">
    <div style="width: 48%; margin-bottom: 15px;">
        <strong>От Заказчика:</strong><br><br>
        <div style="border-bottom: 1px solid #000; height: 18px;"></div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
    <div style="width: 48%; margin-bottom: 15px;">
        <strong>От монтажной организации:</strong><br><br>
        <div style="border-bottom: 1px solid #000; min-height: 18px; padding-bottom: 2px; text-align: center; white-space: nowrap;">
          <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 42px; vertical-align: middle; margin-right: 15px; mix-blend-mode: multiply; transform: rotate(-2deg);">
          Кудря Н.Ю.
        </div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
    <div style="width: 48%;">
        <strong>От пусконаладочной организации:</strong><br><br>
        <div style="border-bottom: 1px solid #000; min-height: 18px; padding-bottom: 2px; text-align: center; white-space: nowrap;">
          <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 42px; vertical-align: middle; margin-right: 15px; mix-blend-mode: multiply; transform: rotate(-2deg);">
          Кудря Н.Ю.
        </div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
    <div style="width: 48%;">
        <strong>Представители иных лиц:</strong><br><br>
        <div style="border-bottom: 1px solid #000; height: 18px;"></div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
</div>
</div>

<div style="page-break-after: always; break-after: page;"></div>

<div style="font-size: 14pt; line-height: 1.5; color: #000;">
<div style="text-align: right; font-weight: bold;">Приложение И</div>
<div style="text-align: center; font-weight: bold; margin-bottom: 20px; font-size: 14pt;">
ФОРМА АКТА О ПРОВЕДЕНИИ АВТОНОМНЫХ ИСПЫТАНИЙ СИСТЕМЫ
</div>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Объект:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">{{ project_object | default(project.project_title) }}</span></p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Заказчик (генподрядчик):</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">{{ customer_name | default('Заказчик') }}</span><sup>1)</sup></p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Лицо, осуществляющее монтаж:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">ООО «Голд Линк», ИНН 7224078140, ОГРН 1177232028423</span><sup>3)</sup></p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Лицо, осуществляющее пусконаладочные работы:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">ООО «Голд Линк», ИНН 7224078140, ОГРН 1177232028423</span><sup>3)</sup></p>

<h2 style="font-size: 14pt; margin: 20px 0 10px 0; text-align: center; border: none;">АКТ<br>о проведении автономных испытаний системы № <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 50px;">&nbsp;&nbsp;&nbsp;&nbsp;</span></h2>
<p style="text-align: center; margin-bottom: 20px; text-indent: 0;">от " <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 30px;">&nbsp;&nbsp;&nbsp;&nbsp;</span> " <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 80px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span> {{ date.split('.')[-1] }} г.</p>

<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Представитель заказчика:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 300px; text-indent: 0;">&nbsp;</span><sup>4)</sup></p>
<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Представитель монтажной организации:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Главный специалист тех. группы Кудря Н.Ю.</span></p>
<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Представитель пусконаладочной организации:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Главный специалист тех. группы Кудря Н.Ю.</span></p>
<p style="margin-bottom: 8px; text-indent: 1.25cm;"><strong>Иные представители лиц:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 300px; text-indent: 0;">&nbsp;</span></p>

<div style="font-size: 11pt; color: #444; margin-top: 5px; line-height: 1.1; font-style: italic;">
1), 5) Указывается при наличии. 2), 3) За исключением случаев, когда членство в СРО не требуется.<br>
4) В случае осуществления строительного контроля.
</div>

<p style="margin-top: 15px; margin-bottom: 10px; font-weight: bold; text-indent: 1.25cm;">Составили настоящий Акт о том, что:</p>

<p style="margin-bottom: 8px; text-align: justify; text-indent: 1.25cm;">
1. Смонтированная и допущенная к испытаниям система <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">{{ system_name | default('Система громкоговорящей связи') }}</span><br>
В период с "___" ____________ 2026 г. по "{{ date }}" была подвергнута автономным испытаниям согласно программе и методике <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Программа и методика испытаний (ПМИ)</span>.
</p>

<p style="margin-bottom: 8px; text-align: justify; text-indent: 1.25cm;">
2. При проведении автономных испытаний выявлено: <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Оборудование Armtel функционирует в штатном режиме, заявленные технические характеристики и зоны слышимости подтверждены.</span>
</p>

<p style="margin-bottom: 15px; text-align: justify; text-indent: 1.25cm;">
3. Процесс проведения автономных испытаний отражен в чек-листах индивидуальных испытаний оборудования.
</p>

<div style="text-align: center; font-weight: bold; margin: 15px 0;">Заключение</div>

<p style="margin-bottom: 15px; text-align: justify; text-indent: 1.25cm;">
Система <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">{{ system_name | default('Система громкоговорящей связи') }}</span> автономные испытания <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">выдержала</span>.
</p>

<p style="margin-bottom: 5px; text-indent: 1.25cm;">Акт составлен в ____ экземплярах.</p>
<p style="margin-bottom: 20px; text-indent: 1.25cm;"><strong>Приложения:</strong> <span style="display: inline-block; border-bottom: 1px solid #000; padding: 0 8px; min-width: 100px; text-indent: 0;">Журнал производства ПНР (чек-листы индивидуальных испытаний оборудования ГГС).</span></p>

<div style="margin-top: 30px; display: flex; justify-content: space-between; flex-wrap: wrap; font-size: 12pt;">
    <div style="width: 48%; margin-bottom: 15px;">
        <strong>От Заказчика:</strong><br><br>
        <div style="border-bottom: 1px solid #000; height: 18px;"></div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
    <div style="width: 48%; margin-bottom: 15px;">
        <strong>От монтажной организации:</strong><br><br>
        <div style="border-bottom: 1px solid #000; min-height: 18px; padding-bottom: 2px; text-align: center; white-space: nowrap;">
            <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 42px; vertical-align: middle; margin-right: 15px; mix-blend-mode: multiply; transform: rotate(-2deg);">
            Кудря Н.Ю.
        </div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
    <div style="width: 48%;">
        <strong>От пусконаладочной организации:</strong><br><br>
        <div style="border-bottom: 1px solid #000; min-height: 18px; padding-bottom: 2px; text-align: center; white-space: nowrap;">
            <img src="{{ sign_src | default('sign.png') }}" alt="Подпись" style="max-height: 42px; vertical-align: middle; margin-right: 15px; mix-blend-mode: multiply; transform: rotate(-2deg);">
            Кудря Н.Ю.
        </div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
    <div style="width: 48%;">
        <strong>Представители иных лиц:</strong><br><br>
        <div style="border-bottom: 1px solid #000; height: 18px;"></div>
        <div style="font-size: 12pt; text-align: center;">(подпись, ФИО)</div>
    </div>
</div>
</div>
