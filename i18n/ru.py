# -*- coding: utf-8 -*-
"""The Russian dictionary, kept as data and spliced into the prototype.

EXACT: whole strings the reader sees. PATTERNS: the same, but with numbers,
names or dates inside — a regex with $1, $2 … carried through untouched.
{1:день|дня|дней} picks the Russian plural from capture 1; $*1 sends a capture
back through the dictionary.

Re-extracted on 2026-10-08 from the tables inside
prototype/shelfcall-all-roles.html, which had grown past this file while the
prototype was being worked on as an artifact. Edit here, then run
    python3 i18n/build_i18n.py
to write the tables back into the master.
"""

EXACT = {
    'Expand menu':
        'Развернуть меню',
    'Collapse menu':
        'Свернуть меню',
    'Shelfcall courier · Yerevan':
        'Курьер Shelfcall · Ереван',
    'Reader · Yerevan':
        'Читатель · Ереван',
    '1 branch · Yerevan':
        '1 филиал · Ереван',
    '2 branches · Yerevan':
        '2 филиала · Ереван',
    '3 branches · Yerevan':
        '3 филиала · Ереван',
    'Waiting':
        'Ждут',
    'To courier':
        'Курьеру',
    'Nothing here':
        'Здесь пусто',
    'No orders in this state right now.':
        'Сейчас нет заказов в этом статусе.',
    'Pay now':
        'Заплатить сейчас',
    'Pay later':
        'Заплатить позже',
    'Pickup':
        'Самовывоз',
    'To find':
        'Найти',
    'Waiting for buyer':
        'Ждут покупателя',
    'With courier':
        'У курьера',
    'To deliver':
        'Доставить',
    'Take these off the shelf and mark them ready.':
        'Снимите с полки и отметьте как готовые.',
    'Put aside. The buyer pays at the counter and gives four digits.':
        'Отложены. Покупатель платит у кассы и называет четыре цифры.',
    'Ready. A courier will come and pay you for them.':
        'Готовы. Курьер заберёт и заплатит вам.',
    'On the way to the buyer. Nothing for you to do.':
        'В пути к покупателю. От вас ничего не нужно.',
    'Go round the shops. Pay each one as its card says.':
        'Объедьте магазины. Платите каждому, как указано в карточке.',
    'Everything is on you. Hand it over and take the cash.':
        'Всё у вас. Передайте заказ и возьмите деньги.',
    'Nothing to deliver yet':
        'Пока нечего доставлять',
    'Every order is on you. Switch to To deliver.':
        'Все заказы у вас. Перейдите в «Доставить».',
    'Collect from the shops first.':
        'Сначала заберите из магазинов.',
    'still to pay the shops':
        'ещё отдать магазинам',
    'of delivery fees for the office':
        'сборов за доставку для офиса',
    'Your cash':
        'Ваши деньги',
    'Still to pay the shops':
        'Ещё отдать магазинам',
    'Delivery fees for the office':
        'Сборы за доставку для офиса',
    'Delivery fees to hand in at the office':
        'Сборы за доставку — сдать в офис',
    'Already paid to the shop.':
        'Магазину уже заплачено.',
    'Collect it from the shop first.':
        'Сначала заберите из магазина.',
    'not yet paid to the shop':
        'магазину ещё не заплачено',
    'Pick up everything before you go.':
        'Заберите всё, прежде чем ехать.',
    'unread':
        'не прочитано',
    'Rate':
        'Оценить',
    'Not now':
        'Не сейчас',
    'Its offers are set aside. Ordering one closes it too.':
        'Предложения будут отложены. Заказ по одному из них тоже закрывает запрос.',
    'It leaves the shops’ feed. You can ask again any time.':
        'Запрос уйдёт из ленты магазинов. Спросить снова можно в любой момент.',
    'Add to cart to take it with books from your other requests.':
        'Добавьте в корзину, чтобы взять вместе с книгами по другим запросам.',
    'Not charged — free month.':
        'Не начисляется — бесплатный месяц.',
    'Book money only. Commission is on your statement.':
        'Только деньги за книги. Комиссия — в вашем счёте.',
    'Delivered; the courier still has the cash. Anything older than a day, tell us.':
        'Доставлено, деньги ещё у курьера. Если прошло больше дня — сообщите нам.',
    'Final for this application.':
        'Окончательно для этой заявки.',
    'Paid in cash':
        'Оплачено наличными',
    'The courier pays you':
        'Курьер заплатит вам',
    'Cash at the counter':
        'Наличными у кассы',
    'Keep it wrapped by the counter.':
        'Держите упакованной у кассы.',
    'The reader is told and their request reopens.':
        'Читателю сообщат, его запрос снова откроется.',
    'One notice with a link to rate you. You can ask once.':
        'Одно уведомление со ссылкой на оценку. Попросить можно один раз.',
    'Earned':
        'Заработано',
    'To collect':
        'К получению',
    'History':
        'История',
    'Delivered, cash still with the courier':
        'Доставлено, деньги ещё у курьера',
    'The courier pays you after the buyer has paid. Anything older than a day, tell us.':
        'Курьер платит вам после оплаты покупателем. Если прошло больше дня — сообщите нам.',
    'Open orders':
        'Открытые заказы',
    'Yours once the book is handed over.':
        'Станут вашими, когда книга будет передана.',
    'How billing works':
        'Как работают счета',
    '14 days':
        '14 дней',
    '30 days':
        '30 дней',
    'Tap a day for its numbers.':
        'Нажмите на день, чтобы увидеть цифры.',
    'Book money only. Commission is billed separately, on your statement.':
        'Только деньги за книги. Комиссия выставляется отдельно, в вашем счёте.',
    'Nothing to collect':
        'Получать нечего',
    'to find and mark ready':
        'найти и отметить готовым',
    'waiting for the buyer':
        'ждёт покупателя',
    '← Billing':
        '← Счета',
    'in your till':
        'в кассе',
    'See To collect.':
        'См. «К получению».',
    'Your code · say it at the counter':
        'Ваш код · назовите его у кассы',
    'Change the delivery time':
        'Изменить время доставки',
    'Possible until a shop marks the book ready. The courier is given the new time.':
        'Можно, пока магазин не отметил книгу готовой. Курьер получит новое время.',
    'Keep this time':
        'Оставить это время',
    'Cancelled · nothing to pay.':
        'Отменён · платить ничего не нужно.',
    'Your request is open again, and the other offers on it are back.':
        'Ваш запрос снова открыт, другие предложения по нему вернулись.',
    'Live':
        'Активные',
    'Sold':
        'Проданы',
    'Closed':
        'Закрыты',
    'Sold elsewhere — take down':
        'Продано в другом месте — снять',
    'Yes, it is gone':
        'Да, снимаю',
    'Not chosen, taken down or set aside. Kept for your record.':
        'Не выбраны, сняты или отложены. Хранятся для истории.',
    'Nothing closed':
        'Закрытых нет',
    'Nothing sold yet':
        'Пока ничего не продано',
    'Nothing live right now':
        'Сейчас активных нет',
    'Answer a request and your offer waits here until the reader orders.':
        'Ответьте на запрос — предложение подождёт здесь, пока читатель не закажет.',
    'Open the feed':
        'Открыть ленту',
    'being checked':
        'на проверке',
    'Find and mark ready':
        'Найти и отметить готовым',
    'Oldest first. The cash comes to you at handover.':
        'Сначала самые старые. Деньги — при передаче.',
    'Waiting for the buyer':
        'Ждут покупателя',
    'Put aside for pickup. They show a four-digit code.':
        'Отложены для самовывоза. Покупатель покажет четырёхзначный код.',
    'Courier coming':
        'Курьер в пути',
    'Wrapped and by the counter.':
        'Упакованы и лежат у кассы.',
    'With the courier':
        'У курьера',
    'with the courier':
        'у курьера',
    'Nothing more for you to do.':
        'От вас больше ничего не нужно.',
    'A buyer at the counter?':
        'Покупатель у кассы?',
    'Buyer at the counter?':
        'Покупатель у кассы?',
    'Type their four digits and their order opens.':
        'Введите его четыре цифры — откроется его заказ.',
    'Find':
        'Найти',
    'No order put aside here has that code. Ask them to read it again.':
        'Среди отложенных заказов нет такого кода. Попросите прочитать ещё раз.',
    "Buyer's code":
        'Код покупателя',
    'Results':
        'Результаты',
    'How your shop answers the requests that reach it.':
        'Как ваш магазин отвечает на запросы, которые до него доходят.',
    '4 weeks':
        '4 недели',
    '12 weeks':
        '12 недель',
    'All time':
        'За всё время',
    'Reached you':
        'Дошли до вас',
    'requests that went out while you were open':
        'запросы, отправленные, пока вы работали',
    'Opened':
        'Открыто',
    'Offered a book':
        'Предложена книга',
    'Became an order':
        'Стало заказом',
    'the Shelfcall average, all shops together':
        'среднее по Shelfcall, все магазины вместе',
    'no opening times yet':
        'времени открытия пока нет',
    'nothing offered yet':
        'пока ничего не предложено',
    'no requests went out in this time':
        'за это время запросов не было',
    'Of':
        'Из',
    'requests that reached you, you opened':
        'запросов, дошедших до вас, вы открыли',
    ', offered a book on':
        ', предложили книгу на',
    ', and':
        ', и',
    'became orders.':
        'стали заказами.',
    'became an order.':
        'стал заказом.',
    'Where you lose the most.':
        'Где вы теряете больше всего.',
    'Most requests close before you see them. Opening the feed twice a day is the quickest win.':
        'Большинство запросов закрываются раньше, чем вы их видите. Открывайте ленту дважды в день — это самый быстрый выигрыш.',
    'You open requests but rarely answer. A close match is worth sending — readers often take “something like it”.':
        'Вы открываете запросы, но редко отвечаете. Близкое совпадение стоит отправить — читатели часто берут «что-то похожее».',
    'Readers choose other copies over yours. Clear photos of the actual copy and a fair price win most often.':
        'Читатели выбирают другие экземпляры. Чаще всего выигрывают чёткие фото самого экземпляра и честная цена.',
    'Every step is at or above the average.':
        'Каждый шаг на уровне среднего или выше.',
    'Keep answering quickly — speed is what readers notice first.':
        'Отвечайте так же быстро — скорость читатели замечают первой.',
    'Nothing has reached you yet':
        'До вас пока ничего не дошло',
    'Once requests start reaching your feed, this shows how many you open, answer and sell.':
        'Когда запросы начнут приходить в ленту, здесь будет видно, сколько вы открываете, отвечаете и продаёте.',
    'See it and buy':
        'Посмотреть и купить',
    'Newest':
        'Сначала новые',
    'Cheapest':
        'Сначала дешёвые',
    'Best condition':
        'Лучшее состояние',
    'Best rated':
        'Лучший рейтинг',
    'How it reaches you':
        'Как книга до вас дойдёт',
    'Pick it up':
        'Забрать самому',
    'No pickup at this branch.':
        'В этом филиале самовывоза нет.',
    'Buy goes straight to checkout. Add to cart to take it together with books from your other requests.':
        '«Купить» ведёт сразу к оформлению. «В корзину» — чтобы взять вместе с книгами по другим запросам.',
    'Want more answers?':
        'Хотите больше ответов?',
    'A higher limit, or any condition, reaches more copies. Close this request and ask again with them — nothing you wrote is lost.':
        'Более высокий лимит или любое состояние находят больше экземпляров. Закройте запрос и спросите снова — ничего из написанного не потеряется.',
    'Books from this shop':
        'Книги из этого магазина',
    'Edit details':
        'Изменить данные',
    'Change time':
        'Изменить время',
    'Nothing within your limit of':
        'В пределах вашего лимита',
    'yet. The copies above it are below.':
        'пока ничего нет. Экземпляры дороже — ниже.',
    'waiting for your check':
        'ждёт вашей проверки',
    'Light':
        'Светлая',
    'Busy':
        'Много',
    'Test it':
        'Проверить',
    'a few requests, offers and orders':
        'немного запросов, предложений и заказов',
    ' before your shop opens':
        ' до открытия магазина',
    '+ Add a location':
        '+ Добавить точку',
    '. The courier calls before arriving.':
        '. Курьер позвонит перед приездом.',
    '1 month ago':
        'месяц назад',
    '2 weeks ago':
        '2 недели назад',
    '3 weeks ago':
        '3 недели назад',
    'A Shelfcall courier collects it from you.':
        'Курьер Shelfcall заберёт её у вас.',
    'A book you are describing':
        'Книга, которую вы описываете',
    'A book you can name':
        'Книга, которую вы можете назвать',
    'A job appears when a shop marks an order ready.':
        'Задание появляется, когда магазин отмечает заказ готовым.',
    'A line on your statement that looks wrong does not need a phone call — flag it on the billing screen and it is held out of the total until someone looks.':
        'Из-за сомнительной строки в счёте звонить не нужно — отметьте её на экране счёта, и она не попадёт в итог, пока кто-то не разберётся.',
    'A mad-scientist novel, funny rather than grim — the narrator is the experiment. Short, 180 pages.':
        'Роман про безумного учёного, скорее смешной, чем мрачный — рассказчик и есть эксперимент. Коротко, 180 страниц.',
    'A new account has no name, phone or address, no requests and no orders — which is what every empty screen in this app is written for.':
        'У нового аккаунта нет ни имени, ни телефона, ни адреса, ни запросов, ни заказов — ради этого и написан каждый пустой экран.',
    'A new request':
        'Новый запрос',
    'A person checks every shop before it opens — usually the same day. Your free month starts with your first offer, not today.':
        'Каждый магазин перед открытием проверяет человек — обычно в тот же день. Бесплатный месяц начнётся с вашего первого предложения, а не сегодня.',
    'A problem with a book you received is better raised on the order itself — it holds the shop’s commission until someone looks.':
        'О проблеме с полученной книгой лучше сказать прямо в заказе — это удержит комиссию магазина, пока кто-то не разберётся.',
    'A reader is watching this — if you cannot do it, say so, and their request reopens straight away.':
        'Читатель следит за этим — если не получается, скажите, и его запрос сразу откроется снова.',
    'A request you pass on is kept here rather than thrown away. Nothing is lost by missing one.':
        'Запрос, который вы пропустили, хранится здесь, а не удаляется. Пропустить — не значит потерять.',
    'A subject, a mood, half a memory. Shops answer with what they think fits and say why — you are choosing between their judgement as much as their prices.':
        'Тема, настроение, обрывок воспоминания. Магазины отвечают тем, что считают подходящим, и объясняют почему — вы выбираете не только цену, но и их суждение.',
    'A title, at least. Everything else is optional.':
        'Хотя бы название. Всё остальное необязательно.',
    'About an order, a delivery, or a bookseller. A person answers, not a form.':
        'О заказе, доставке или книготорговце. Отвечает человек, а не форма.',
    'About an order, a statement, or your shop’s details. A person answers, not a form.':
        'О заказе, счёте или данных вашего магазина. Отвечает человек, а не форма.',
    'About the shop':
        'О магазине',
    'Account':
        'Аккаунт',
    'Add':
        'Добавить',
    'Add a photo':
        'Добавить фото',
    'Add another book':
        'Добавить ещё книгу',
    'Add location':
        'Добавить точку',
    'Add photo':
        'Добавить фото',
    'Add to cart':
        'В корзину',
    'Address in Yerevan':
        'Адрес в Ереване',
    'After delivery':
        'После доставки',
    'All':
        'Все',
    'All months':
        'Все месяцы',
    'All optional. A reader hunting a particular printing looks for exactly this.':
        'Всё необязательно. Читатель, который ищет конкретное издание, смотрит именно на это.',
    'All your orders':
        'Все ваши заказы',
    'Also going with this offer':
        'Тоже уйдёт с этим предложением',
    'An order arrives when a reader takes one of your offers.':
        'Заказ приходит, когда читатель берёт одно из ваших предложений.',
    'An order counts from the moment it is handed over.':
        'Заказ считается с момента передачи книги.',
    'Answer a request first':
        'Сначала ответьте на запрос',
    'Anything by Sei Shōnagon. The Pillow Book ideally, any translation.':
        'Что-нибудь Сэй-Сёнагон. Лучше «Записки у изголовья», в любом переводе.',
    'Anything else?':
        'Что-нибудь ещё?',
    'Anything the next buyer should know? (optional)':
        'Что стоит знать следующему покупателю? (необязательно)',
    'Appearance':
        'Внешний вид',
    'Approve and place the order':
        'Подтвердить и оформить заказ',
    'Approving closes the requests these books answered, and releases the other offers on them.':
        'Подтверждение закрывает запросы, на которые отвечают эти книги, и освобождает остальные предложения по ним.',
    'Apr':
        'апр.',
    'April':
        'апрель',
    'Are you sure?':
        'Вы уверены?',
    'Art books about Armenian miniatures — the older the printing the better.':
        'Альбомы об армянской миниатюре — чем старее издание, тем лучше.',
    'As described':
        'Как в описании',
    'As soon as possible':
        'Как можно скорее',
    'Ask again with a clock':
        'Спросить снова с часами',
    'Ask for a book':
        'Попросить книгу',
    'Ask, and the shops answer':
        'Спросите — магазины ответят',
    'Aug':
        'авг.',
    'August':
        'август',
    'Author':
        'Автор',
    'Back':
        'Назад',
    'Back in the deck':
        'Снова в колоде',
    'Back on top of the deck':
        'Снова сверху колоды',
    'Back to the deck':
        'Назад к колоде',
    'Back to the feed':
        'Вернуться в ленту',
    'Billing':
        'Счёт',
    'Binding':
        'Переплёт',
    'Book as described. Had to wait two days before it was ready.':
        'Книга как в описании. Пришлось подождать два дня, пока подготовят.',
    'Bookseller':
        'Книготорговец',
    'Booksellers are looking for your book.':
        'Книготорговцы ищут вашу книгу.',
    'Both numbers are with us — nothing has been recorded as paid':
        'Обе суммы у нас — ничего не записано как оплаченное',
    'Both reach every bookseller in Yerevan. They answer them differently.':
        'Оба уходят каждому книготорговцу Еревана. Отвечают на них по-разному.',
    'Branch':
        'Точка',
    'Buy':
        'Купить',
    'Call':
        'Позвонить',
    'Cancel':
        'Отмена',
    'Cancel this order?':
        'Отменить заказ?',
    'Cancelled — the cash is still yours':
        'Отменено — деньги по-прежнему у вас',
    'Cart':
        'Корзина',
    'Cash':
        'Наличные',
    'Cash from the courier':
        'Наличные от курьера',
    'Change something':
        'Изменить',
    'Cheapest of the three offers and the book was fine.':
        'Самое дешёвое из трёх предложений, и книга в порядке.',
    'Check':
        'Проверка',
    'Check the offer':
        'Проверить предложение',
    'Check the order':
        'Проверить заказ',
    'Checkout':
        'Оформить',
    'Chosen':
        'Выбрано',
    'City':
        'Город',
    'Close this request':
        'Закрыть запрос',
    'Close this request?':
        'Закрыть запрос?',
    'Collect them from the shops first':
        'Сначала заберите из магазинов',
    'Collected':
        'Забран',
    'Collected from the shop':
        'Забрал из магазина',
    'Commission at 12%':
        'Комиссия 12%',
    'Completed and cancelled orders are kept here, with what you paid and who you paid it to.':
        'Выполненные и отменённые заказы хранятся здесь — вместе с тем, сколько и кому вы заплатили.',
    'Completed and cancelled orders are kept here.':
        'Выполненные и отменённые заказы хранятся здесь.',
    'Condition':
        'Состояние',
    'Condition and price':
        'Состояние и цена',
    'Continue':
        'Далее',
    'Continue with this photo':
        'Продолжить с этим фото',
    'Continue without a photo':
        'Продолжить без фото',
    'Could not deliver':
        'Не смог доставить',
    'Count it first. Typing the code is you saying you have it.':
        'Сначала пересчитайте. Ввод кода — это ваше подтверждение, что деньги у вас.',
    'Counted and recorded — both of you signed for it':
        'Пересчитано и записано — подтвердили оба',
    'Counted something else? Put in what you actually took — the two numbers go to us with both your names on them.':
        'Пересчитали другую сумму? Укажите, сколько вы действительно взяли — обе цифры уйдут к нам, с вашими именами.',
    'Courier':
        'Курьер',
    'Courier · Shelfcall team · Yerevan':
        'Курьер · команда Shelfcall · Ереван',
    'Cover worn at the corners, text block sound. Scientists, and quite mad by the end.':
        'Углы обложки потёрты, блок крепкий. Учёные, и к финалу вполне безумные.',
    'Dark':
        'Тёмная',
    'Dec':
        'дек.',
    'December':
        'декабрь',
    'Default delivery address':
        'Адрес доставки по умолчанию',
    'Deliver to':
        'Доставить',
    'Delivered':
        'Доставлено',
    'Deliveries':
        'Доставки',
    'Deliveries you close are kept here with the cash.':
        'Закрытые доставки хранятся здесь вместе с деньгами.',
    'Delivery':
        'Доставка',
    'Delivery is ours to run and ours to price — 1 000 ֏ per order, whatever it holds. You are paid for the books.':
        'Доставка — наша забота и наша цена: 1 000 ֏ за заказ, сколько бы книг в нём ни было. Вам платят за книги.',
    'Delivery time':
        'Время доставки',
    'Describe a book — a title, or only what you remember. Booksellers across Yerevan look on their shelves and reply with real copies.':
        'Опишите книгу — название или только то, что помните. Книготорговцы по всему Еревану посмотрят на полках и ответят настоящими экземплярами.',
    'Describe a book. Booksellers answer with what is on their shelves.':
        'Опишите книгу. Книготорговцы ответят тем, что стоит у них на полках.',
    'Done':
        'Готово',
    'Earnings':
        'Выручка',
    'Edit':
        'Изменить',
    'Edit it first if you can — the same words will come back the same way.':
        'Сначала исправьте, если есть что — те же слова вернутся так же.',
    'Edit this book':
        'Изменить эту книгу',
    'Editing your offer':
        'Редактирование предложения',
    'Edition':
        'Издание',
    'Email':
        'Эл. почта',
    'Every bookshop in Yerevan has it, with a loud notification.':
        'Запрос у всех книжных Еревана, с громким уведомлением.',
    'Every offer says which branch the book is on. You need at least one.':
        'В каждом предложении указано, на какой точке книга. Нужна хотя бы одна.',
    'Every shop in the city can see it now, not only the ones in good standing.':
        'Теперь запрос виден всем магазинам города, а не только тем, у кого всё в порядке.',
    'Everything collected.':
        'Всё забрано.',
    'Everything open has had an answer from you, one way or the other.':
        'На каждый открытый запрос вы так или иначе ответили.',
    'Exactly the edition I hoped for, wrapped in paper. Handed over next day.':
        'Ровно то издание, на которое я надеялась, завёрнутое в бумагу. Передали на следующий день.',
    'Fair price':
        'Честная цена',
    'Fast':
        'Быстро',
    'Feb':
        'фев.',
    'February':
        'февраль',
    'Feed':
        'Лента',
    'Fill the fields above and this opens.':
        'Заполните поля выше, и кнопка откроется.',
    'Find the book first, then mark it ready below.':
        'Сначала найдите книгу, потом отметьте готовность ниже.',
    'Finished':
        'Завершённые',
    'Five photographs is as many as a reader will look at.':
        'Пять фотографий — больше читатель всё равно не смотрит.',
    'Fix it and send again':
        'Исправить и отправить снова',
    'Following your phone':
        'Как на телефоне',
    'Follows whatever your phone is set to right now.':
        'Следует текущей настройке вашего телефона.',
    'Foxing on the endpapers, otherwise clean.':
        'Пятна на форзацах, в остальном чисто.',
    'Give it a price — that is what the reader compares.':
        'Поставьте цену — именно её сравнивает читатель.',
    'Give us the order number if it is about one — it is at the top of every order page.':
        'Назовите номер заказа, если вопрос о нём, — он вверху страницы заказа.',
    'Grouped by the request they answer. An offer stays live until the reader orders — no clock, no expiry.':
        'Сгруппированы по запросам, на которые отвечают. Предложение живёт, пока читатель не закажет, — ни часов, ни срока.',
    'Handed the cash over?':
        'Деньги переданы?',
    'Help':
        'Помощь',
    'How should the courier pay you?':
        'Как курьеру платить вам?',
    'I cannot do this one':
        'Не смогу с этой',
    'I understand':
        'Понятно',
    "I'm wondering about a book with a crazy scientist — fiction, not too heavy. Something I could read in a week.":
        'Ищу книгу про сумасшедшего учёного — художественную, не слишком тяжёлую. Такую, чтобы прочесть за неделю.',
    'If nobody can do it in time nothing is lost — the request keeps going without the clock.':
        'Если никто не успеет, ничего не потеряно — запрос продолжит жить без часов.',
    'If there is only one copy on your shelf, take it down there — otherwise another reader can order a book you have just sold.':
        'Если экземпляр на полке один, снимите его и там — иначе другой читатель закажет уже проданную книгу.',
    'If you think this is a mistake, reply to the email we sent you and a person will read it.':
        'Если считаете это ошибкой, ответьте на наше письмо — его прочитает человек.',
    'In the app':
        'В приложении',
    'In your hands':
        'На руках',
    'In your till':
        'В вашей кассе',
    'It happens — a walk-in customer got there first. Say which, and we will tell the reader straight away':
        'Бывает — покупатель в зале успел раньше. Скажите, что случилось, и мы сразу сообщим читателю',
    'It is waiting in your cart. Press it again to take it out.':
        'Лежит в корзине. Нажмите ещё раз, чтобы убрать.',
    'It is yours to hold for as long as you want to — put it back whenever you decide the buyer is not coming.':
        'Держите столько, сколько считаете нужным — верните на полку, когда решите, что покупатель не придёт.',
    'It starts when they open':
        'Начнётся, когда откроются',
    'It stops being offered on new books. Offers already on it are untouched.':
        'Её перестанут предлагать для новых книг. Уже выставленные предложения не трогаем.',
    'Jan':
        'янв.',
    'January':
        'январь',
    'Jul':
        'июл.',
    'July':
        'июль',
    'Jun':
        'июн.',
    'June':
        'июнь',
    'Keep it':
        'Оставить',
    'Keep this and check the order':
        'Оставить и проверить заказ',
    'Kept for next time, so you only do this once.':
        'Сохраним на будущее, чтобы вводить один раз.',
    'Language':
        'Язык',
    'Mar':
        'мар.',
    'March':
        'март',
    'Master and Margarita — the 1988 edition, or anything close to it.':
        '«Мастер и Маргарита» — издание 1988 года или что-нибудь близкое.',
    'Master and Margarita, the 1988 edition.':
        '«Мастер и Маргарита», издание 1988 года.',
    'Match my phone':
        'Как на телефоне',
    'May':
        'май',
    'Miss':
        'Пропустить',
    'Missed':
        'Пропущенные',
    'Missed — kept in the archive':
        'Пропущено — сохранено в архиве',
    'More about this copy':
        'Подробнее об экземпляре',
    'More about this copy — optional':
        'Подробнее об экземпляре — необязательно',
    'My offers':
        'Мои предложения',
    'Name':
        'Имя',
    'Nearly there.':
        'Почти готово.',
    'New jobs come to you':
        'Новые задания приходят вам',
    'New offers, order updates, review reminders':
        'Новые предложения, изменения заказов, напоминания об отзывах',
    'New requests are not reaching you while the statement is unpaid.':
        'Новые запросы не доходят до вас, пока счёт не оплачен.',
    'New requests stop reaching you until it is settled. Your open offers and running orders are not affected.':
        'Новые запросы перестают доходить, пока счёт не оплачен. На ваши действующие предложения и текущие заказы это не влияет.',
    'New seller':
        'Новый продавец',
    'Next — when should it come?':
        'Дальше — когда доставить?',
    'No deadline. It stays open until you order from it or close it, and offers never expire — a hard book can take weeks and still turn up.':
        'Без срока. Запрос живёт, пока вы не закажете по нему или не закроете, и предложения не сгорают — редкая книга может найтись и через несколько недель.',
    'No deliveries right now':
        'Сейчас доставок нет',
    'No more price changes on this offer.':
        'Цену этого предложения больше менять нельзя.',
    'No orders yet':
        'Заказов пока нет',
    'No photo of this copy.':
        'Фото этого экземпляра нет.',
    'No reviews yet':
        'Отзывов пока нет',
    'No title — they described it':
        'Без названия — описали словами',
    'No, I did not':
        'Нет, не получил',
    'Nobody could do it in time.':
        'Никто не успел вовремя.',
    'None of them are still open.':
        'Ни один из них уже не открыт.',
    'Norwegian Wood, any edition, English or Russian.':
        '«Норвежский лес», любое издание, на английском или русском.',
    'Not collected — put it back':
        'Не забрали — вернуть на полку',
    'Not now — cancel':
        'Не сейчас — отменить',
    'Note about this copy':
        'Заметка об экземпляре',
    'Note for the courier (optional)':
        'Заметка курьеру (необязательно)',
    'Nothing arrived under that reference.':
        'По этому номеру ничего не пришло.',
    'Nothing delivered yet':
        'Пока ничего не доставлено',
    'Nothing due':
        'Ничего не должны',
    'Nothing finished yet':
        'Пока ничего не завершено',
    'Nothing finished yet.':
        'Пока ничего не завершено.',
    'Nothing has counted yet':
        'Пока ничего не учтено',
    'Nothing in the cart':
        'Корзина пуста',
    'Nothing is charged here. You pay cash, shop by shop, when each book reaches you.':
        'Здесь ничего не списывается. Вы платите наличными, магазин за магазином, когда книга доедет.',
    'Nothing is owed during the free month — this is what it would have been.':
        'В бесплатный месяц платить нечего — это то, сколько было бы.',
    'Nothing missed yet':
        'Пока ничего не пропущено',
    'Nothing missed yet.':
        'Пока ничего не пропущено.',
    'Nothing needs you':
        'Ничего не ждёт вас',
    'Nothing on its way':
        'Ничего в пути',
    'Nothing open right now':
        'Сейчас нет открытых запросов',
    'Nothing to bring back':
        'Возвращать нечего',
    'Nothing waiting on you':
        'Ничего не ждёт вас',
    'Notifications':
        'Уведомления',
    'Nov':
        'ноя.',
    'November':
        'ноябрь',
    'ORDER PLACED':
        'ЗАКАЗ ОФОРМЛЕН',
    'Oct':
        'окт.',
    'October':
        'октябрь',
    'Offer':
        'Предложить',
    'Offer a book':
        'Предложить книгу',
    'Offer a book from your shelves':
        'Предложить книгу со своих полок',
    'Offer a book from your shelves, or miss it — what you miss is kept.':
        'Предложите книгу со своих полок или пропустите — пропущенное сохраняется.',
    'Offer another book':
        'Предложить ещё книгу',
    'Offer sent':
        'Предложение отправлено',
    'Offers and order changes appear here.':
        'Здесь появляются предложения и изменения по заказам.',
    'Offers you add from your requests land here.':
        'Предложения, которые вы добавите из своих запросов, попадут сюда.',
    'Offers you send stay here until a reader orders.':
        'Отправленные предложения живут здесь, пока читатель не закажет.',
    'Once it is read you can still lower the price or say more — the book itself is fixed from then on.':
        'После прочтения можно снизить цену или добавить описание — сама книга с этого момента зафиксирована.',
    'Once you order from a request it closes and moves to Orders.':
        'Как только вы закажете по запросу, он закроется и уйдёт в «Заказы».',
    'One hour while you are open. Find the book first, then mark it ready below.':
        'Один час, пока вы открыты. Сначала найдите книгу, потом отметьте готовность ниже.',
    'One paragraph. It is the first thing a reader reads on your profile.':
        'Один абзац. Это первое, что читатель читает в вашем профиле.',
    'One thing to fix':
        'Нужно одно исправление',
    'One thing to fix before your shop opens.':
        'Одно исправление — и магазин откроется.',
    'One trip per address. A shop is a stop on it.':
        'Одна поездка на адрес. Магазин — остановка на ней.',
    'Online only. Science fiction, mostly Soviet-era printings.':
        'Только онлайн. Фантастика, в основном советских изданий.',
    'Only press this with the book put aside. The buyer gets your address, your hours and a four-digit code.':
        'Нажимайте, только когда книга отложена. Покупатель получит ваш адрес, часы работы и четырёхзначный код.',
    'Only press this with the book wrapped and on the counter. A courier is sent for it.':
        'Нажимайте, только когда книга завёрнута и лежит на прилавке. За ней отправят курьера.',
    'Only the courier sees this note. The bookseller never does.':
        'Эту заметку видит только курьер. Книготорговец — никогда.',
    'Open':
        'Открыть',
    'Open one to see the books and say it is ready. The cash comes to you at handover.':
        'Откройте заказ, посмотрите книги и отметьте готовность. Деньги вы получаете при передаче.',
    'Open the camera':
        'Открыть камеру',
    'Open the order':
        'Открыть заказ',
    'Open-ended':
        'Свободный',
    'Optional, but it is the only thing telling this reader apart from a list of prices — they did not name a book.':
        'Необязательно, но только это отличает вас от списка цен — читатель не назвал книгу.',
    'Or choose a time':
        'Или выберите время',
    'Or write':
        'Или напишите',
    'Order events only — never offers':
        'Только события заказа — никогда предложения',
    'Order placed':
        'Заказ оформлен',
    'Ordering from this request closes it and releases the other offers.':
        'Заказ по этому запросу закрывает его и освобождает остальные предложения.',
    'Orders':
        'Заказы',
    'Orders you place stay here until the book is in your hands.':
        'Оформленные заказы остаются здесь, пока книга не окажется у вас.',
    'Orders you place stay here until the book reaches you.':
        'Оформленные заказы остаются здесь, пока книга не доедет до вас.',
    'Out of your own pocket':
        'Из своего кармана',
    'Pages':
        'Страниц',
    'Paid to shops':
        'Отдано магазинам',
    'Past its hour.':
        'Час истёк.',
    'Pay the courier, all of it at once':
        'Заплатите курьеру — всё сразу',
    'Pay the shop now instead':
        'Лучше заплатить магазину сейчас',
    'Payment':
        'Оплата',
    'Penguin Classics, read once.':
        'Penguin Classics, читали один раз.',
    'Phone':
        'Телефон',
    'Photo':
        'Фото',
    'Photo removed':
        'Фото убрано',
    'Photo saved':
        'Фото сохранено',
    'Photograph the copy':
        'Сфотографируйте экземпляр',
    'Photos of the actual copy':
        'Фотографии самого экземпляра',
    'Photos of this copy':
        'Фото этого экземпляра',
    'Pick a reason first':
        'Сначала выберите причину',
    'Pick it up, then bring it to the buyer.':
        'Заберите и отвезите покупателю.',
    'Pick this if you are home anyway. The courier calls before arriving, and comes as soon as every shop has been collected from.':
        'Выберите, если вы всё равно дома. Курьер позвонит перед приездом и приедет, как только заберёт книги из всех магазинов.',
    'Pick up from':
        'Забрать из',
    'Picked up from':
        'Забрано из',
    'Placed':
        'Оформлен',
    'Price':
        'Цена',
    'Prototype — see this as':
        'Прототип — смотреть как',
    'Publish review':
        'Опубликовать отзыв',
    'Published — the shops can see it now':
        'Опубликовано — магазины уже видят',
    'Publisher':
        'Издательство',
    'Put in the amount you actually counted.':
        'Укажите сумму, которую вы действительно пересчитали.',
    'Put it back in the deck':
        'Вернуть в колоду',
    'Put it back on the shelf?':
        'Вернуть на полку?',
    'Read the code out — nothing is recorded until they type it':
        'Продиктуйте код — пока его не введут, ничего не записано',
    'Read them':
        'Читать',
    'Read this out':
        'Продиктуйте это',
    'Read this out at the counter.':
        'Назовите его на кассе.',
    'Reader':
        'Читатель',
    'Ready for delivery':
        'Готово к доставке',
    'Ready for pickup':
        'Готово к самовывозу',
    'Ready to collect':
        'Готов к выдаче',
    'Reason':
        'Причина',
    'Remove':
        'Убрать',
    'Remove photo':
        'Убрать фото',
    'Remove — sold':
        'Убрать — продано',
    'Removed — it is gone from the reader’s list':
        'Снято — у читателя его больше нет',
    'Request':
        'Запрос',
    'Request closed':
        'Запрос закрыт',
    'Requests':
        'Запросы',
    'Retire this branch?':
        'Закрыть эту точку?',
    'Retire this location':
        'Закрыть эту точку',
    'Reviews':
        'Отзывы',
    'SHOP BY SHOP':
        'ПО МАГАЗИНАМ',
    'Save':
        'Сохранить',
    'Save changes':
        'Сохранить изменения',
    'Say it now and the courier is stood down before the trip. The reader is told and their request reopens':
        'Скажите сейчас — и курьера отзовут до выезда. Читателю сообщат, а его запрос откроется снова',
    'Second entrance, gate code 4417. Call rather than ring.':
        'Второй подъезд, код 4417. Лучше позвоните по телефону.',
    'Second entrance, the gate code is 4417. Call rather than ring — the bell is broken.':
        'Второй подъезд, код 4417. Лучше позвоните по телефону — домофон сломан.',
    'Second-hand shop near Mashtots. Strong on Russian classics, art books and 70s–90s translations.':
        'Букинистический у Маштоца. Сильны в русской классике, альбомах по искусству и переводах 70–90-х.',
    'Send it to us again':
        'Отправить снова',
    'Send request':
        'Отправить запрос',
    'Send the offer':
        'Отправить предложение',
    'Sent':
        'Отправлено',
    'Sent three photos before I bought. No surprises when it arrived.':
        'Прислали три фотографии до покупки. Никаких сюрпризов при получении.',
    'Sent — a person checks every shop before it opens':
        'Отправлено — каждый магазин перед открытием проверяет человек',
    'Sent — we read it before the shops do':
        'Отправлено — мы читаем его раньше магазинов',
    'Sep':
        'сен.',
    'September':
        'сентябрь',
    'Settings':
        'Настройки',
    'Settle with the shop later instead':
        'Лучше рассчитаться с магазином позже',
    'Shift':
        'Смена',
    'Shop by shop':
        'По магазинам',
    'Shop name':
        'Название магазина',
    'Shops ready':
        'Магазины готовы',
    'Showing a brand new account':
        'Показываем совсем новый аккаунт',
    'Sign out':
        'Выйти',
    'Skip for now':
        'Пропустить',
    'Small stall, mostly English paperbacks and Penguin editions.':
        'Небольшая точка, в основном английские покеты и издания Penguin.',
    'Solaris, the Mir printing if you have it.':
        '«Солярис», издание «Мира», если есть.',
    'Sold through Shelfcall':
        'Продано через Shelfcall',
    'Something happened to the book':
        'С книгой что-то случилось',
    'Something is wrong':
        'Здесь что-то не так',
    'Something is wrong with this line':
        'С этой строкой что-то не так',
    'Something like Borges but easier going. Short stories, a bit strange, nothing too dense.':
        'Что-нибудь вроде Борхеса, но полегче. Рассказы, слегка странные, не слишком плотные.',
    'Something like…':
        'Что-нибудь вроде…',
    'Something with a crazy scientist, not too heavy.':
        'Что-нибудь про сумасшедшего учёного, не слишком тяжёлое.',
    'Specific':
        'Конкретная',
    'Spine slightly faded, pages clean, no marks. From a 1979 Moscow print run.':
        'Корешок слегка выцвел, страницы чистые, без пометок. Московская печать 1979 года.',
    'Start another whenever a book comes to mind.':
        'Начните новый, как только вспомните книгу.',
    'Step 1 of 2 · your details':
        'Шаг 1 из 2 · ваши данные',
    'Still looking. Hard books take longer, and nothing here expires.':
        'Ещё ищут. Редкие книги ищутся дольше, а срока здесь нет.',
    'Still owed to you':
        'Вам ещё должны',
    'Still waiting on the shops.':
        'Ждём ответа магазинов.',
    "Stopped looking? Closing it takes the request off the shops' feed. You can post it again any time.":
        'Больше не ищете? Закрытие убирает запрос из ленты магазинов. Опубликовать снова можно в любой момент.',
    'Stopped looking? Closing it takes the request off the shops’ feed. You can post it again any time.':
        'Больше не ищете? Закрытие убирает запрос из ленты магазинов. Опубликовать снова можно в любой момент.',
    'Swipe the card, or use the buttons.':
        'Смахните карточку или нажмите кнопку.',
    'Take in cash at the counter':
        'Наличными на кассе',
    'Take it out':
        'Убрать',
    'Take out of cart':
        'Убрать из корзины',
    'Take the book, pay nothing.':
        'Заберите книгу, платить не нужно.',
    'Take the payment claim back?':
        'Отозвать заявление об оплате?',
    'Take this offer down':
        'Снять предложение',
    'Take this offer down?':
        'Снять это предложение?',
    'Taken back':
        'Отозвано',
    'Taken from buyers':
        'Взято у покупателей',
    'Taken out of this offer':
        'Убрано из предложения',
    'Taking deliveries':
        'Беру доставки',
    'Tell them a little more — ten characters at least.':
        'Расскажите чуть больше — хотя бы десять символов.',
    'Tell us what your shelves are strong on and we will point those requests at you.':
        'Скажите, на чём сильны ваши полки, и мы будем направлять такие запросы вам.',
    'That is not the amount':
        'Сумма другая',
    'That is not the code on the courier’s phone. Ask them to read it again.':
        'Это не тот код, что на экране у курьера. Попросите продиктовать ещё раз.',
    'The 1988 printing you asked for. Dust jacket intact.':
        'То самое издание 1988 года. Суперобложка цела.',
    'The Pillow Book — any decent edition.':
        '«Записки у изголовья» — любое приличное издание.',
    'The book':
        'Книга',
    'The bookseller needs a name to hold the book under.':
        'Книготорговцу нужно имя, на которое отложить книгу.',
    'The buyer did not collect it. The order closes, their request reopens, and the copy is yours again.':
        'Покупатель не забрал. Заказ закрывается, его запрос открывается снова, а экземпляр снова ваш.',
    'The courier calls before arriving.':
        'Курьер позвонит перед приездом.',
    'The courier collected it':
        'Курьер забрал',
    'The courier pays when they collect':
        'Курьер платит, когда забирает книгу',
    'The courier settles after delivery':
        'Курьер рассчитывается после доставки',
    'The courier settles after the buyer has paid. Anything older than a day, tell us.':
        'Курьер рассчитывается после того, как заплатит покупатель. Если прошло больше суток — скажите нам.',
    'The courier settles this with them':
        'Курьер рассчитается с ними',
    'The courier settles this with you':
        'Курьер рассчитается с вами',
    'The courier takes the book, collects the buyer’s cash and pays you afterwards. Less cash moving around.':
        'Курьер забирает книгу, берёт наличные у покупателя и платит вам после. Меньше наличных в обороте.',
    'The first one arrives after your first finished order.':
        'Первый появится после вашего первого завершённого заказа.',
    'The foxing, the spine, the jacket — this is what a reader is really choosing between.':
        'Пятна, корешок, суперобложка — именно по этому читатель и выбирает.',
    'The name readers see on every offer you send.':
        'Имя, которое читатели видят в каждом вашем предложении.',
    'The reader has been told':
        'Читателю сообщили',
    'The reader has been told — their request is open again':
        'Читателю сообщили — его запрос снова открыт',
    'The reader stops seeing this copy. If it is in their cart it disappears from it, and they are told.':
        'Читатель перестанет видеть этот экземпляр. Если он в корзине — исчезнет оттуда, и читателю сообщат.',
    'The shop has to find the book and a courier has to collect it, so the earliest we will promise is':
        'Магазину нужно найти книгу, а курьеру — забрать её, поэтому раньше мы не обещаем:',
    'The shop is owed':
        'Магазину причитается',
    'The shop is told, the request reopens and the other offers on it come back.':
        'Магазину сообщат, запрос откроется снова, и остальные предложения по нему вернутся.',
    'The shops have been told again':
        'Магазинам сообщили ещё раз',
    'The shops have had your request for a day. Hard-to-find books often take longer — nothing expires.':
        'Запрос у магазинов уже сутки. Редкие книги часто ищут дольше — ничего не сгорает.',
    'The shops stop seeing it, and any offers on it are set aside. Nothing is deleted — you keep the record, and you can post it again any time.':
        'Магазины перестанут его видеть, а предложения по нему отложатся. Ничего не удаляется — запись остаётся у вас, и запрос можно опубликовать снова в любой момент.',
    'There is nothing for you to do until then. We will tell you the moment the first one arrives, and offers never expire, so you can take your time comparing them.':
        'До этого от вас ничего не нужно. Мы сообщим, как только придёт первое предложение, — они не сгорают, так что сравнивайте спокойно.',
    'They are reminded tomorrow and again the day after.':
        'Им напомнят завтра и ещё раз послезавтра.',
    'They asked for':
        'Просят:',
    'They asked for up to':
        'Просят: до',
    'They confirm it when the book is in their hands. If it sits here too long, tell us and we will chase it.':
        'Магазин подтвердит, когда книга будет у него в руках. Если затянется — скажите нам, мы поторопим.',
    'They did not come. Put it back on the shelf whenever you like.':
        'Не пришли. Верните на полку, когда сочтёте нужным.',
    'This is what':
        'Вот что увидит',
    'This offer is closed':
        'Это предложение закрыто',
    'This request is closed — the reader ordered or stopped looking.':
        'Запрос закрыт — читатель заказал или перестал искать.',
    'Title':
        'Название',
    'To do':
        'К работе',
    'Track order':
        'Следить за заказом',
    'Translation is under way. Anything not translated yet stays in English rather than being machine-translated — you can see what is done and what is not.':
        'Перевод в работе. Всё, что ещё не переведено, остаётся на английском, а не переводится машинно, — видно, что готово, а что нет.',
    'Type the four digits the courier is showing you.':
        'Введите четыре цифры, которые показывает курьер.',
    'Untitled':
        'Без названия',
    'Used when you order. Changing them never touches an order already placed.':
        'Используются при заказе. Изменение не затрагивает уже оформленные заказы.',
    'View public profile':
        'Открыть публичный профиль',
    'WHERE IT IS':
        'ГДЕ ЗАКАЗ',
    'WHO IT GOES TO':
        'КОМУ УЙДЁТ',
    'We are checking your shop.':
        'Мы проверяем ваш магазин.',
    'We are reading your request. It goes to the shops as soon as it is through — usually within the hour.':
        'Мы читаем ваш запрос. Он уйдёт в магазины, как только пройдёт проверку — обычно в течение часа.',
    'We cannot open this shop':
        'Мы не можем открыть этот магазин',
    'We cannot open this shop.':
        'Мы не можем открыть этот магазин.',
    'We sent this back to you.':
        'Мы вернули вам этот запрос.',
    'We stop looking for it. Your statement goes back to unpaid.':
        'Мы перестанем его искать. Счёт снова станет неоплаченным.',
    'Well packed':
        'Хорошо упаковано',
    'What are your shelves good for?':
        'Чем сильны ваши полки?',
    'What buyers see, where your books are, and how the courier settles with you.':
        'Что видят покупатели, где стоят ваши книги и как с вами рассчитывается курьер.',
    'What buyers wrote after a handover. You cannot delete them — and neither can we.':
        'Что покупатели написали после передачи книги. Вы не можете их удалить — и мы тоже.',
    'What kind of asking is this?':
        'Какого рода этот запрос?',
    'What readers are asking for that you have not answered yet. Once you send an offer the request moves to':
        'Что просят читатели и на что вы ещё не ответили. Как только вы отправите предложение, запрос уйдёт в',
    'What they asked for':
        'Что они просят',
    'What you are carrying':
        'Что вы везёте',
    'What you are picking up':
        'Что вы забираете',
    'What you sent':
        'Что вы отправили',
    'What you take for books shows up here, by day and by month.':
        'Здесь видно, сколько вы получаете за книги, по дням и по месяцам.',
    'What you took for books, month by month. Commission is not taken out of these — it is billed separately above.':
        'Сколько вы взяли за книги, месяц за месяцем. Комиссия отсюда не вычитается — она выставляется отдельно выше.',
    'What your shelves are good for':
        'Чем сильны ваши полки',
    'When does the courier pay you?':
        'Когда курьер платит вам?',
    'When should it come?':
        'Когда доставить?',
    'When they collect':
        'При получении',
    'Where are the books?':
        'Где стоят книги?',
    'Where it is':
        'Где заказ',
    'Where should it go?':
        'Куда доставить?',
    'Where the courier says it is paid, confirm it in Orders and it moves across.':
        'Где курьер отметил оплату — подтвердите в «Заказах», и сумма перейдёт сюда.',
    'Which book is it?':
        'Что это за книга?',
    'Which book is it? A title, at least.':
        'Что за книга? Хотя бы название.',
    'Which book?':
        'Какая книга?',
    'Which branch is this copy on?':
        'На какой точке этот экземпляр?',
    'Who is collecting?':
        'Кто забирает?',
    'Who it goes to':
        'Кому уйдёт',
    'Why this book answers them':
        'Почему эта книга им подойдёт',
    'Why this one':
        'Почему именно эта',
    'Why this one?':
        'Почему именно эта?',
    'YOUR CASH TODAY':
        'ВАШИ ДЕНЬГИ СЕГОДНЯ',
    'Year':
        'Год',
    'Yerevan':
        'Ереван',
    'Yes, I got it':
        'Да, получил',
    'Yes, back on the shelf':
        'Да, обратно на полку',
    'Yes, close it':
        'Да, закрыть',
    'Yes, do it':
        'Да, сделать',
    'You already have one open with them':
        'С ними у вас уже есть открытая передача',
    'You are Dina, in Yerevan.':
        'Вы — Дина, Ереван.',
    'You are reminded the day before with the amount, and the statement is issued and due on the day itself. Unpaid that night and new requests stop reaching you — except the ones nobody else answered in 72 hours. You pay, then tell us here with a reference — that lifts it straight away while an operator matches it against the bank.':
        'Накануне мы напомним сумму, а сам счёт выставляется и подлежит оплате в тот же день. Не оплачен к ночи — новые запросы перестают до вас доходить, кроме тех, на которые за 72 часа никто не ответил. Вы платите, затем говорите нам здесь с номером платежа — это снимает ограничение сразу, пока оператор сверяет платёж с банком.',
    'You can add more, or take them out, at any point before this goes.':
        'Добавить или убрать фото можно в любой момент до отправки.',
    'You can add one later, before the offer goes. A copy with a photograph is chosen far more often.':
        'Фото можно добавить позже, до отправки предложения. Экземпляр с фотографией выбирают гораздо чаще.',
    'You can change it until a shop marks the book ready.':
        'Можно менять, пока магазин не отметит книгу готовой.',
    'You can change this on the next screen.':
        'Это можно изменить на следующем экране.',
    'You can edit a review for 24 hours. Skipping is fine — we will not ask again.':
        'Отзыв можно изменить в течение 24 часов. Пропустить — нормально: больше не спросим.',
    'You can see how many others answered, never what they asked for it.':
        'Вы видите, сколько ещё магазинов ответили, но никогда — их цены.',
    'You collect these yourself, each with its own four-digit code.':
        'Вы забираете их сами, у каждого свой четырёхзначный код.',
    "You do not see the buyer's name, phone or address on a delivery, and you never will — the courier has them. You are paid for the book; where it ends up is our leg of the trip.":
        'На доставке вы не видите имени, телефона и адреса покупателя — и не увидите: они у курьера. Вам платят за книгу; куда она поедет — наш отрезок пути.',
    'You get it back from the buyer on delivery.':
        'Вернёте себе с покупателя при доставке.',
    'You have been through the whole deck':
        'Вы прошли всю колоду',
    'You have not answered anything yet':
        'Вы ещё ни на что не ответили',
    'You know the title, or the author, or the edition. Shops check the shelf and answer with that book — you compare copies, condition and price.':
        'Вы знаете название, автора или издание. Магазины смотрят на полке и отвечают именно этой книгой — вы сравниваете экземпляры, состояние и цену.',
    'You will pay the shop at pickup':
        'Вы заплатите магазину при получении',
    'You will settle with the shop later':
        'Вы рассчитаетесь с магазином позже',
    'Your application':
        'Ваша заявка',
    'Your cash today':
        'Ваши деньги сегодня',
    'Your details':
        'Ваши данные',
    'Your first branch. You can add more later, and every offer says which one holds the copy.':
        'Ваша первая точка. Позже можно добавить ещё, и в каждом предложении видно, где лежит экземпляр.',
    'Your history':
        'Ваша история',
    'Your live offers':
        'Ваши живые предложения',
    'Your offers':
        'Ваши предложения',
    'Your own month, billed on the 15th — 12% of what you actually sold here, books only, delivery never counted.':
        'Ваш собственный месяц, счёт 15-го — 12% от того, что вы здесь действительно продали: только книги, доставка никогда не считается.',
    'Your price':
        'Ваша цена',
    'Your request':
        'Ваш запрос',
    'Your request is already with them; the clock starts when the first shop opens.':
        'Запрос уже у них; часы пойдут, когда откроется первый магазин.',
    'Your request is still open — it just has no clock on it now. Shops answer hard ones in their own time, and nothing here expires.':
        'Запрос по-прежнему открыт — просто на нём больше нет часов. Сложные ищут в своём темпе, и здесь ничего не сгорает.',
    'Your request is with the booksellers.':
        'Ваш запрос у книготорговцев.',
    'Your requests':
        'Ваши запросы',
    'Your shop':
        'Ваш магазин',
    'Your shop is open':
        'Ваш магазин открыт',
    'Your shopfront, a shelf, your logo. Until you add one, buyers see your initials — never a stock picture.':
        'Витрина, полка, логотип. Пока фото нет, покупатели видят ваши инициалы — никогда не стоковую картинку.',
    'a brand new account':
        'совсем новый аккаунт',
    'a courier collects it':
        'заберёт курьер',
    'a reader with history':
        'читатель с историей',
    'amounts disagree':
        'суммы не сходятся',
    'as':
        'как',
    'boxed set':
        'в футляре',
    'buyers may collect':
        'можно забрать',
    'cancelled':
        'отменён',
    'cancelled the order':
        'отменил заказ',
    'cannot find it':
        'не могу найти',
    'cash on delivery':
        'наличными при доставке',
    'changed my mind':
        'передумал',
    'checking':
        'проверяем',
    'closed — too late':
        'закрыт — поздно',
    'collected in the shop':
        'забрано в магазине',
    'confirmed your order':
        'подтвердил ваш заказ',
    'courier says paid':
        'курьер отметил оплату',
    'damaged':
        'повреждена',
    'done':
        'готово',
    'due':
        'к оплате',
    'each shop confirms separately':
        'каждый магазин подтверждает отдельно',
    'good standing':
        'всё в порядке',
    'handed it to the courier':
        'передал курьеру',
    'handing over now':
        'передаётся сейчас',
    'hardcover':
        'твёрдый',
    'has it ready for the courier':
        'подготовил для курьера',
    'has it ready to collect':
        'подготовил к выдаче',
    'in a cart':
        'в корзине',
    'in your bag':
        'у вас в сумке',
    'leather':
        'кожаный',
    'new seller':
        'новый продавец',
    'no answer':
        'не открыли',
    'no author given':
        'автор не указан',
    'no comment':
        'без комментария',
    'no pickup':
        'без самовывоза',
    'no pickup here':
        'здесь без самовывоза',
    'nobody has answered':
        'никто не ответил',
    'not as described':
        'не как в описании',
    'not chosen':
        'не выбрано',
    'not collected':
        'не забрано',
    'not delivered':
        'не доставлено',
    'not ordered yet':
        'ещё не заказано',
    'not written yet':
        'пока не написано',
    'not yet':
        'ещё рано',
    'nothing due':
        'ничего не должно',
    'on its way':
        'в пути',
    'on the way to you':
        'едет к вам',
    'one trip, whatever the order holds':
        'одна поездка, сколько бы книг ни было',
    'paid':
        'оплачено',
    'paid at pickup':
        'оплачено при получении',
    'paid at the counter':
        'оплата на кассе',
    'paid in cash at the door':
        'оплата наличными у двери',
    'paperback':
        'мягкий',
    'price or grade':
        'цена или состояние',
    'ready for the courier':
        'готово для курьера',
    'refused it':
        'отказались',
    'request fulfilled':
        'запрос исполнен',
    'requests reach you from now on':
        'теперь вам приходят запросы',
    'restricted':
        'ограничено',
    'sent back':
        'вернули',
    'set aside':
        'отложено',
    'shop paid':
        'магазину заплачено',
    'shop paid at pickup':
        'магазину заплачено при получении',
    'so far':
        'пока',
    'sold':
        'продано',
    'sold in the shop':
        'продана в магазине',
    'street, building, apartment':
        'улица, дом, квартира',
    'the buyer collects it':
        'покупатель заберёт сам',
    'the copy is gone':
        'экземпляра больше нет',
    'the courier brings it':
        'привезёт курьер',
    'they stay live until you order':
        'живут, пока вы не закажете',
    'to collect':
        'забрать',
    'to deliver':
        'доставить',
    'trial':
        'пробный период',
    'waiting':
        'ждём',
    'waiting for cash':
        'ждём наличные',
    'waiting for you':
        'ждёт вас',
    'waiting on the courier':
        'ждём курьера',
    'waiting on the shop':
        'ждём магазин',
    'wrong address':
        'неверный адрес',
    'you answered this':
        'вы на него ответили',
    'your code is below':
        'ваш код ниже',
    '— not yet':
        '— ещё рано',
    '← All months':
        '← Все месяцы',
    '← Book 1':
        '← Книга 1',
    '← Book 2':
        '← Книга 2',
    '← Book 3':
        '← Книга 3',
    '← Cart':
        '← Корзина',
    '← Deliveries':
        '← Доставки',
    '← My offers':
        '← Мои предложения',
    '← Order':
        '← Заказ',
    '← Orders':
        '← Заказы',
    '← Request':
        '← Запрос',
    '← Requests':
        '← Запросы',
    '← The book':
        '← Книга',
    '← The deck':
        '← Колода',
    '← The last book':
        '← Последняя книга',
    '← The photo':
        '← Фото',
    '← Why this one':
        '← Почему именно она',
    '▸ open':
        '▸ открыть',
    '▸ read it again':
        '▸ перечитать',
    '▸ read it back':
        '▸ перечитать',
    '▸ read what they asked':
        '▸ читать, что просили',
    '▸ see the books':
        '▸ посмотреть книги',
    '▾ close':
        '▾ закрыть',
    '▾ fold it away':
        '▾ свернуть',
    '▾ hide the books':
        '▾ скрыть книги',
    '▾ hide the details':
        '▾ скрыть подробности',
    '▾ hide what they asked':
        '▾ скрыть, что просили',
    '✓ In cart':
        '✓ В корзине',
}

PATTERNS = [
    ('^· buyer pays (.+)$',
     '· покупатель платит $1'),
    ('^(\\d+) shops? · (\\d+) books?$',
     'магазинов: $1 · книг: $2'),
    ('^You owe the shop (.+) after delivery\\.$',
     'После доставки вы должны магазину $1.'),
    ('^(\\d+) of (\\d+) shops still to collect from\\.$',
     'Ещё забрать в $1 из $2 магазинов.'),
    ('^(.+) still owed to you$',
     'Вам ещё должны $1'),
    ('^(\\d+) still open$',
     'Ещё открыто: $1'),
    ('^How was (.+)\\?$',
     'Как прошло с $1?'),
    ('^Take (.+), then type their four digits$',
     'Возьмите $1 и введите четыре цифры покупателя'),
    ('^The courier comes for it (.+)\\. Mark it ready as soon as it is wrapped\\.$',
     'Курьер приедет $1. Отметьте готовность, как только упакуете.'),
    ('^(\\d+) live offers? here$',
     'Активных предложений здесь: $1'),
    ('^You asked for a review (.+) ago\\. One ask per order\\.$',
     'Вы попросили отзыв $1 назад. Одна просьба на заказ.'),
    ('^Earned, last (\\d+) days$',
     'Заработано за $1 дн.'),
    ('^(\\d+) orders? handed over$',
     'Передано заказов: $1'),
    ('^— delivered, the courier still has the cash\\. See To collect\\.$',
     '— доставлено, деньги ещё у курьера. См. «К получению».'),
    ('^(.+) still owed to you$',
     'Вам ещё должны $1'),
    ('^New time: (.+)$',
     'Новое время: $1'),
    ('^A shop has already marked it ready — the time is fixed now$',
     'Магазин уже отметил готовность — время зафиксировано'),
    ('^One courier, one trip: they collect from (\\d+) shops and bring everything together\\.$',
     'Один курьер, одна поездка: заберёт из $1 магазинов и привезёт всё вместе.'),
    ('^usually (.+) after it went out · average shop (\\d+)%$',
     'обычно через $1 после отправки · в среднем $2%'),
    ('^usually (.+) after it went out$',
     'обычно через $1 после отправки'),
    ('^(\\d+)% of what you opened · first offer usually (.+) after it went out · average shop (\\d+)%$',
     '$1% от открытых · первое предложение обычно через $2 · в среднем $3%'),
    ('^(\\d+)% of what you opened · first offer usually (.+) after it went out$',
     '$1% от открытых · первое предложение обычно через $2'),
    ('^(\\d+)% of what you opened · average shop (\\d+)%$',
     '$1% от открытых · в среднем $2%'),
    ('^(\\d+) of (\\d+) answered requests \\((\\d+)%\\) · average shop (\\d+)%$',
     '$1 из $2 отвеченных запросов ($3%) · в среднем $4%'),
    ('^(\\d+) of (\\d+) answered requests \\((\\d+)%\\)$',
     '$1 из $2 отвеченных запросов ($3%)'),
    ('^(nothing offered yet|no opening times yet) · average shop (\\d+)%$',
     'пока нет данных · в среднем $2%'),
    ('^(\\d+) requests? waiting in your feed$',
     'В ленте ждут запросов: $1'),
    ('^(\\d+) offers? · (\\d+) new · they stay live until you order$',
     '$1 {1:предложение|предложения|предложений} · новых: $2 · живут, пока вы не закажете'),
    ('^Show (\\d+) over your limit · from (.+)$',
     'Показать дороже лимита: $1 · от $2'),
    ('^Over your limit of (.+)$',
     'Дороже вашего лимита $1'),
    ('^over your limit of (.+)$',
     'дороже вашего лимита $1'),
    ('^· free · (.+)\\. You show a four-digit code\\.$',
     '· бесплатно · $1. Покажете четырёхзначный код.'),
    ('^· (.+) for the whole order, one trip — even with books from other shops\\. You pay cash at the door\\.$',
     '· $1 за весь заказ, одна поездка — даже с книгами из других магазинов. Оплата наличными у двери.'),
    ('^Seen by (\\d+) of (\\d+) bookshops so far\\.$',
     'Уже видели $1 из $2 магазинов.'),
    ('^(\\d+) handovers? from one shop$',
     'Передач: $1, из одного магазина'),
    ('^(\\d+) handovers?$',
     'Передач: $1'),
    ('^(\\d+) handovers? from (\\d+) shops$',
     'Передач: $1, из $2 магазинов'),
    ('^Start checking · (\\d+)$',
     'Начать проверку · $1'),
    ('^For (\\d+) orders? \\u00b7 (.+)\\. Count it first\\. Typing the code is you saying you have it\\.$',
     'За $1 {1:заказ|заказа|заказов} · $2. Сначала пересчитайте. Ввод кода — это ваше подтверждение, что деньги у вас.'),
    ('^Hand over ([\\d\\u00a0 ]+\\u058f)$',
     'Передать $1'),
    ('^Got it \\u00b7 ([\\d\\u00a0 ]+\\u058f)$',
     'Получил · $1'),
    ('^(.+) is handing you ([\\d\\u00a0 ]+\\u058f)$',
     '$1 передаёт вам $2'),
    ('^(\\d+) orders? in one go\\. They confirm with a code at the counter\\.$',
     'Заказов сразу: $1. Они подтверждают кодом на месте.'),
    ('^Free month \\u00b7 (\\d+) days left$',
     'Бесплатный месяц · осталось дней: $1'),
    ('^, then 12% of what you sell\\.$',
     ', потом 12% от проданного.'),
    ('^Your free month ends in (\\d+) days?$',
     'Бесплатный месяц заканчивается через $1 {1:день|дня|дней}'),
    ('^\\. Offer another (?:price or grade|price|grade) if that is what is on your shelf \\u2014 they decide, and a copy they can see beats nothing\\.$',
     '. Предложите другую цену или состояние, если на полке именно такое — решать им, а экземпляр, который видно, лучше, чем ничего.'),
    ('^This is what (.+) will see\\. Nothing has been sent yet \\u2014 open a book to read it back, or edit it\\.$',
     'Вот что увидит $1. Пока ничего не отправлено — откройте книгу, чтобы перечитать или исправить.'),
    ('^(\\d+) requests? you passed on\\. (\\d+) of them (?:is|are) still open \\u2014 a shop that finds the book a week later is still the shop that found it\\.$',
     'Запросов, которые вы пропустили: $1. Из них ещё открыто: $2 — магазин, нашёдший книгу через неделю, — всё равно тот, кто её нашёл.'),
    ('^(\\d+) requests? you passed on\\. None of them are still open\\.$',
     'Запросов, которые вы пропустили: $1. Ни один из них уже не открыт.'),
    ('^(\\d+) waiting on you$',
     'ждут вас: $1'),
    ('^(\\d+) shops? answered$',
     'ответили магазинов: $1'),
    ('^\\u21ba Bring back (.+)$',
     '↺ Вернуть «$*1»'),
    ('^Missed \\u00b7 (\\d+)$',
     'Пропущенные · $1'),
    ('^Look through the (\\d+) you missed$',
     'Посмотреть $1 пропущенных'),
    ('^(\\d+) requests? you passed on\\.$',
     'Запросов, которые вы пропустили: $1.'),
    ('^(\\d+) of them (?:is|are) still open \\u2014 a shop that finds the book a week later is still the shop that found it\\.$',
     'Из них ещё открыто: $1 — магазин, нашёдший книгу через неделю, — всё равно тот, кто её нашёл.'),
    ('^Continue with (\\d+) photos$',
     'Продолжить с $1 фото'),
    ('^Part (\\d+) of (\\d+) \\u00b7 (.+)$',
     'Часть $1 из $2 · $*3'),
    ('^Book (\\d+) \\u00b7 Part (\\d+) of (\\d+) \\u00b7 (.+)$',
     'Книга $1 · часть $2 из $3 · $*4'),
    ('^Free month \\u00b7 (\\d+) days? left, then 12% of what you actually sell\\.$',
     'Бесплатный месяц · осталось дней: $1, потом 12% от того, что вы действительно продаёте.'),
    ('^(\\d+) new$',
     '$1 {1:новое|новых|новых}'),
    ('^(\\d+) new of (\\d+)$',
     '$1 {1:новое|новых|новых} из $2'),
    ('^tomorrow, (\\d\\d:\\d\\d)$',
     'завтра, $1'),
    ('^today, (\\d\\d:\\d\\d)$',
     'сегодня, $1'),
    ('^tomorrow (\\d\\d:\\d\\d)$',
     'завтра $1'),
    ('^today (\\d\\d:\\d\\d)$',
     'сегодня $1'),
    ('^open (\\d+) days?$',
     'открыт $1 {1:день|дня|дней}'),
    ('^open (\\d+) h$',
     'открыт $1 ч'),
    ('^open (\\d+) min$',
     'открыт $1 мин'),
    ('^up to ([\\d\xa0 ]+֏)$',
     'до $1'),
    ('^(\\d+) offers? · (\\d+) new$',
     '$1 {1:предложение|предложения|предложений} · $2 {2:новое|новых|новых}'),
    ('^(\\d+) offers?$',
     '$1 {1:предложение|предложения|предложений}'),
    ('^no offers yet$',
     'ответов пока нет'),
    ('^still looking$',
     'ещё ищем'),
    ('^open to all shops$',
     'открыт всем магазинам'),
    ('^fulfilled$',
     'исполнен'),
    ('^closed$',
     'закрыт'),
    ('^any condition$',
     'любое состояние'),
    ('^any$',
     'любое'),
    ('^new$',
     'новая'),
    ('^good used$',
     'хорошая б/у'),
    ('^used$',
     'б/у'),
    ('^old$',
     'старая'),
    ('^(\\d+) min left$',
     'осталось $1 {1:минута|минуты|минут}'),
    ('^(\\d+)h (\\d+)m left$',
     'осталось $1 ч $2 мин'),
    ('^Step (\\d+) of (\\d+)$',
     'Шаг $1 из $2'),
    ('^For · step (\\d+) of (\\d+)$',
     'Для · шаг $1 из $2'),
    ('^Book (\\d+) of this offer$',
     'Книга $1 в этом предложении'),
    ('^Book (\\d+) of this offer · step (\\d+) of (\\d+)$',
     'Книга $1 в предложении · шаг $2 из $3'),
    ('^(\\d+) live$',
     '$1 {1:живое|живых|живых}'),
    ('^(\\d+) sold$',
     '$1 продано'),
    ('^(\\d+) books? sent$',
     'отправлено книг: $1'),
    ('^(\\d+) stops?$',
     '$1 {1:остановка|остановки|остановок}'),
    ('^(\\d+) requests? answered$',
     'отвечено на запросов: $1'),
    ('^(\\d+) reviews?$',
     'отзывов: $1'),
    ('^(\\d+) offers? · they stay live until you order$',
     '$1 {1:предложение|предложения|предложений} · живут, пока вы не закажете'),
    ('^Locations \\((\\d+)\\)$',
     'Точки ($1)'),
    ('^Remove ([^.!?]{1,40})$',
     'Убрать $1'),
    ('^Open ([^.!?]{1,60})$',
     'Открыть $1'),
    ('^(.+) asked for$',
     '$1 просит'),
    ('^Free month · (\\d+) days? left\\.$',
     'Бесплатный месяц · осталось дней: $1.'),
    ('^(\\d+) days? left · then 12% of the books total$',
     'осталось дней: $1 · потом 12% от суммы книг'),
    ('^After that, 12% of what you actually sell here\\. Nothing to pay until then\\.$',
     'После этого — 12% от того, что вы здесь действительно продали. До тех пор платить нечего.'),
    ('^Pay ([\\d\xa0 ]+֏)$',
     'Оплатить $1'),
    ('^Delivered · took ([\\d\xa0 ]+֏)$',
     'Доставлено · взял $1'),
    ('^Buy · ([\\d\xa0 ]+֏)$',
     'Купить · $1'),
    ('^Collected · paid ([\\d\xa0 ]+֏)$',
     'Забрал · заплатил $1'),
    ('^([\\d\xa0 ]+֏) in hand$',
     'на руках $1'),
    ('^([\\d\xa0 ]+֏) still owed to you$',
     'вам ещё должны $1'),
    ('^([\\d\xa0 ]+֏) due today$',
     '$1 к оплате сегодня'),
    ('^([\\d\xa0 ]+֏) overdue$',
     '$1 просрочено'),
    ('^([\\d\xa0 ]+֏) sent for checking$',
     '$1 отправлено на проверку'),
    ('^Send for checking$',
     'Отправить на проверку'),
    ('^Take it back$',
     'Забрать обратно'),
    ('^(\\d+) h ago$',
     '$1 ч назад'),
    ('^(\\d+) days? ago$',
     '$1 {1:день|дня|дней} назад'),
    ('^(\\d+) min ago$',
     '$1 мин назад'),
    ('^Monday$',
     'понедельник'),
    ('^Tuesday$',
     'вторник'),
    ('^Wednesday$',
     'среда'),
    ('^Thursday$',
     'четверг'),
    ('^Friday$',
     'пятница'),
    ('^Saturday$',
     'суббота'),
    ('^Sunday$',
     'воскресенье'),
    ('^Today$',
     'Сегодня'),
    ('^Tomorrow$',
     'Завтра'),
    ('^today$',
     'сегодня'),
    ('^tomorrow$',
     'завтра'),
    ('^Within the hour$',
     'В течение часа'),
    ('^30 minutes$',
     '30 минут'),
    ('^Some time today$',
     'Когда-нибудь сегодня'),
    ('^pickup (.+)$',
     'самовывоз $1'),
    ('^courier$',
     'курьер'),
    ('^pickup$',
     'самовывоз'),
    ('^sent$',
     'отправлено'),
    ('^seen$',
     'просмотрено'),
    ('^in cart$',
     'в корзине'),
    ('^completed$',
     'выполнен'),
    ('^cancelled$',
     'отменён'),
    ('^placed$',
     'оформлен'),
    ('^ready$',
     'готов'),
    ('^shipped$',
     'в пути'),
    ('^new seller$',
     'новый продавец'),
    ('^posted (.+)$',
     'опубликовано $*1'),
    ('^sent (.+)$',
     'отправлено $*1'),
    ('^(\\d+) offers? so far$',
     'предложений пока: $1'),
    ('^(\\d+) offers? so far$',
     'предложений пока: $1'),
    ('^Order #(.+)$',
     'Заказ №$1'),
    ('^(.+) \\u2014 (.+) branch$',
     '$1 — филиал $2'),
    ('^(.+) branch$',
     'филиал $1'),
    ('^(.+) \\u2014 Warehouse$',
     '$1 — склад'),
    ('^Warehouse$',
     'Склад'),
    ('^since (.+)$',
     'с $*1'),
    ('^Free until (.+)$',
     'Бесплатно до $*1'),
    ('^This period so far$',
     'Текущий период'),
    ('^Your offers on this request \\((\\d+) live\\)$',
     'Ваши предложения по этому запросу (живых: $1)'),
    ('^Closing it sets aside the (\\d+) offers? above\\. Nothing is deleted \\u2014 you keep the record\\.$',
     'Закрытие отложит предложений выше: $1. Ничего не удаляется — запись остаётся у вас.'),
    ('^(\\d+) of (\\d+) shops? still to collect from\\.$',
     'Осталось забрать из магазинов: $1 из $2.'),
    ('^(\\d+) shops? · (\\d+) books? · ([\\d\\u00a0 ]+֏) cash from the buyer$',
     'магазинов: $1 · книг: $2 · наличными с покупателя $3'),
    ('^(\\d+) books? · the shop is owed ([\\d\\u00a0 ]+֏)$',
     'книг: $1 · магазину причитается $2'),
    ('^(\\d+) orders? · (\\d+) to collect · (\\d+) on you$',
     'заказов: $1 · забрать: $2 · на вас: $3'),
    ('^(\\d+) orders?$',
     '$1 {1:заказ|заказа|заказов}'),
    ('^(\\d+) books?$',
     '$1 {1:книга|книги|книг}'),
    ('^all paid$',
     'всё оплачено'),
    ('^([\\d\\u00a0 ]+֏) still owed$',
     'ещё должны $1'),
    ('^([\\d\\u00a0 ]+֏) paid$',
     'оплачено $1'),
    ('^Commission on this one: ([\\d\\u00a0 ]+֏)$',
     'Комиссия по нему: $1'),
    ('^(\\d+) Jan$',
     '$1 янв.'),
    ('^(\\d+) Feb$',
     '$1 фев.'),
    ('^(\\d+) Mar$',
     '$1 мар.'),
    ('^(\\d+) Apr$',
     '$1 апр.'),
    ('^(\\d+) May$',
     '$1 мая'),
    ('^(\\d+) Jun$',
     '$1 июн.'),
    ('^(\\d+) Jul$',
     '$1 июл.'),
    ('^(\\d+) Aug$',
     '$1 авг.'),
    ('^(\\d+) Sep$',
     '$1 сен.'),
    ('^(\\d+) Oct$',
     '$1 окт.'),
    ('^(\\d+) Nov$',
     '$1 ноя.'),
    ('^(\\d+) Dec$',
     '$1 дек.'),
    ('^January (\\d+)$',
     'январь $1'),
    ('^February (\\d+)$',
     'февраль $1'),
    ('^March (\\d+)$',
     'март $1'),
    ('^April (\\d+)$',
     'апрель $1'),
    ('^May (\\d+)$',
     'май $1'),
    ('^June (\\d+)$',
     'июнь $1'),
    ('^July (\\d+)$',
     'июль $1'),
    ('^August (\\d+)$',
     'август $1'),
    ('^September (\\d+)$',
     'сентябрь $1'),
    ('^October (\\d+)$',
     'октябрь $1'),
    ('^November (\\d+)$',
     'ноябрь $1'),
    ('^December (\\d+)$',
     'декабрь $1'),
    ('^(Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day (\\d+) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$',
     '$2 $*3'),
    ('^tomorrow (\\d\\d:\\d\\d\\u2013\\d\\d:\\d\\d)$',
     'завтра $1'),
    ('^today (\\d\\d:\\d\\d\\u2013\\d\\d:\\d\\d)$',
     'сегодня $1'),
    ('^Tomorrow, (\\d\\d:\\d\\d\\u2013\\d\\d:\\d\\d)$',
     'Завтра, $1'),
    ('^Today, (\\d\\d:\\d\\d\\u2013\\d\\d:\\d\\d)$',
     'Сегодня, $1'),
    ('^After that your day is the (\\d+)(?:st|nd|rd|th) \\u2014 first statement (.+)$',
     'Дальше ваш день — $1-е, первый счёт $*2'),
    ('^Next statement on the (\\d+)(?:st|nd|rd|th) · (.+)$',
     'Следующий счёт $1-го · $*2'),
    ('^held until (.+)$',
     'держим до $*1'),
    ('^confirm by (.+)$',
     'подтвердить до $1'),
    ('^past its hour$',
     'час истёк'),
    ('^courier coming$',
     'курьер в пути'),
    ('^settled$',
     'рассчитано'),
    ('^(\\d+) finished orders? you have not been paid for$',
     'завершённых заказов без оплаты: $1'),
    ('^([\\d\\u00a0 ]+֏) still to pay the shops · ([\\d\\u00a0 ]+֏) of delivery fees for the office$',
     'магазинам ещё платить $1 · $2 сборов за доставку для офиса'),
    ('^The buyer pays ([\\d\\u00a0 ]+֏) when you hand it over\\.$',
     'Покупатель заплатит $1 при передаче.'),
    ('^The buyer asked for (.+) \\u2014 this opens two hours before that\\.$',
     'Покупатель попросил $*1 — кнопка откроется за два часа до этого.'),
    ('^For (.+) \\u2014 not yet$',
     'На $*1 — ещё рано'),
    ('^For (.+)$',
     'На $*1'),
    ('^Take ([\\d\\u00a0 ]+֏) from the buyer\\. ([\\d\\u00a0 ]+֏) of it goes to the shop afterwards\\.$',
     'Возьмите с покупателя $1. Из них $2 потом уйдёт магазину.'),
    ('^Already paid to the shop\\. Take ([\\d\\u00a0 ]+֏) from the buyer and it is square\\.$',
     'Магазину уже заплачено. Возьмите с покупателя $1 — и всё сходится.'),
    ('^Pay the shop ([\\d\\u00a0 ]+֏) when you take the book\\.$',
     'Заплатите магазину $1, когда забираете книгу.'),
    ('^You settle ([\\d\\u00a0 ]+֏) with the shop after you have the buyer\\u2019s cash\\.$',
     'С магазином рассчитаетесь на $1 после того, как получите деньги покупателя.'),
    ('^Ready by (.+)\\.$',
     'Готово к $1.'),
    ('^Prototype with sample data \\u2014 every role is you\\. Reload to start over\\.$',
     'Прототип с демо-данными — все роли это вы. Перезагрузите, чтобы начать заново.'),
    ('^Now showing: (.+)$',
     'Сейчас показано: $*1'),
    ('^Collect at (.+)$',
     'Забрать в $1'),
    ('^Waiting for you at (.+)$',
     'Ждёт вас в $1'),
    ('^collect by (.+)$',
     'забрать до $*1'),
    ('^one open hour to have it ready · (.+)$',
     'один рабочий час на подготовку · $1'),
    ('^tomorrow, (\\d\\d:\\d\\d\\u2013\\d\\d:\\d\\d)$',
     'завтра, $1'),
    ('^today, (\\d\\d:\\d\\d\\u2013\\d\\d:\\d\\d)$',
     'сегодня, $1'),
    ('^(\\d+) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$',
     '$1 $*2'),
    ('^by (\\d\\d:\\d\\d)$',
     'до $1'),
    ('^Ready by (\\d\\d:\\d\\d)\\.$',
     'Готово к $1.'),
    ('^([\\d\\u00a0 ]+֏) cash$',
     'наличными $1'),
    ('^(\\d+) orders? · paid ([\\d\\u00a0 ]+֏) · ([\\d\\u00a0 ]+֏) owed$',
     'заказов: $1 · оплачено $2 · должны $3'),
    ('^([\\d\\u00a0 ]+֏) owed$',
     'должны $1'),
    ('^Of that, ([\\d\\u00a0 ]+֏) still belongs to shops and ([\\d\\u00a0 ]+֏) is delivery fees you hand in at the office\\.$',
     'Из них $1 — деньги магазинов, а $2 — сборы за доставку, которые вы сдаёте в офис.'),
    ('^(\\d+) deliver(?:y|ies) · paid ([\\d\\u00a0 ]+֏) of ([\\d\\u00a0 ]+֏)$',
     'доставок: $1 · оплачено $2 из $3'),
    ('^Delivered \\((\\d+)\\)$',
     'Доставлено ($1)'),
    ('^Could not deliver \\((\\d+)\\)$',
     'Не доставлено ($1)'),
    ('^order #(\\S+) · the shop\\u2019s share ([\\d\\u00a0 ]+֏)$',
     'заказ №$1 · доля магазина $2'),
    ('^Set aside \\((\\d+)\\)$',
     'Отложено ($1)'),
    ('^Finished orders \\((\\d+)\\)$',
     'Завершённые заказы ($1)'),
    ('^(\\d+) books? from (\\d+) shops? · ([\\d\\u00a0 ]+֏) in cash$',
     'книг: $1 из магазинов: $2 · наличными $3'),
    ('^Arriving (.+) · the time you chose\\. The courier calls before arriving\\.$',
     'Приедет $*1 — время, которое вы выбрали. Курьер позвонит перед приездом.'),
    ('^(\\d+) books? · received today$',
     'книг: $1 · получено сегодня'),
    ('^(\\d+) book · received today$',
     'книга получена сегодня'),
    ('^How was (.+)\\?$',
     'Как вам $1?'),
    ('^waiting (\\d+) min$',
     'ждёт $1 мин'),
    ('^waiting (\\d+) h$',
     'ждёт $1 ч'),
    ('^waiting (\\d+) days?$',
     'ждёт $1 {1:день|дня|дней}'),
    ('^put aside (\\d+) min$',
     'отложено $1 мин'),
    ('^put aside (\\d+) h$',
     'отложено $1 ч'),
    ('^put aside (\\d+) days?$',
     'отложено $1 {1:день|дня|дней}'),
    ('^Waiting on you for (\\d+) min\\.$',
     'Ждёт вас $1 мин.'),
    ('^Waiting on you for (\\d+) h\\.$',
     'Ждёт вас $1 ч.'),
    ('^Waiting on you for (\\d+) days?\\.$',
     'Ждёт вас $1 {1:день|дня|дней}.'),
    ('^With the shop for (\\d+) min\\. $',
     'В магазине $1 мин. '),
    ('^With the shop for (.+)\\. (.+)$',
     'В магазине $1. $*2'),
    ('^Put aside (\\d+) min ago\\. $',
     'Отложено $1 мин назад. '),
    ('^Put aside (.+) ago\\. $',
     'Отложено $1 назад. '),
    ('^Put aside for you (.+) ago\\. It is held until you come \\u2014 tell the shop if you need longer\\.$',
     'Отложено для вас $1 назад. Книга ждёт, пока вы не придёте — скажите магазину, если нужно больше времени.'),
    ('^put aside (.+) ago$',
     'отложено $1 назад'),
    ('^find the book and mark it ready$',
     'найдите книгу и отметьте готовность'),
    ('^([\\d\\u00a0 ]+֏) out of your own pocket$',
     '$1 из ваших своих'),
    ('^([\\d\\u00a0 ]+֏) owed \\u2014 settle above$',
     'долг $1 — рассчитайтесь выше'),
    ('^Every shop is checked by a person before it opens \\u2014 usually the same day\\. We tell you here and by email at (.+)\\.$',
     'Каждый магазин перед открытием проверяет человек — обычно в тот же день. Ответ появится здесь и придёт на $1.'),
    ('^Every shop is checked by a person before it opens \\u2014 usually the same day\\. We tell you here and by email\\.$',
     'Каждый магазин перед открытием проверяет человек — обычно в тот же день. Ответ появится здесь и придёт на почту.'),
    ('^It is about: name and photo\\.$',
     'Касается: названия и фото.'),
    ('^It is about: about the shop\\.$',
     'Касается: описания магазина.'),
    ('^It is about: branch\\.$',
     'Касается: точки.'),
    ('^It is about: payment\\.$',
     'Касается: оплаты.'),
    ('^Fix name and photo$',
     'Исправить название и фото'),
    ('^Fix about the shop$',
     'Исправить описание'),
    ('^Fix branch$',
     'Исправить точку'),
    ('^Fix payment$',
     'Исправить оплату'),
]
