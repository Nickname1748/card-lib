class Messages:
    ASSISTANCE = {
        'START': 'Приветствие',
        'INSTRUCTIONS': 'Инструкции',
        'HELP': 'Помощь',
        'CANCEL': 'Операция отменена!',
        'LOADING': 'Пожалуйста, подождите, пока загрузится меню'
    }



    PRIVATE_OFFICE = {
        'INTERFACE': 'Личный кабинет',
    }
    
    PRIVATE_OFFICE_BUTTONS = {
        'Профиль': 'profile',
        'Коллекции': 'collections'
    }



    PROFILE = {
        'INTERFACE': '*Пользователь:* @{}\n*Карма:* {}\n*Коллекций:* {}\n*Карт:* {}'
    }

    PROFILE_BUTTONS = {
        '‹ Назад': 'home'
    }



    COLLECTIONS = {
        'INTERFACE': 'Ваши коллекции:',
        'CREATE_COLLECTION': 'Введите название или ключ коллекции.',
        'COLLECTION_CREATED': 'Вы создали коллекцию «{}».',
        'COLLECTION_COPIED': 'Вы добавили к себе коллекцию «{}».',
        'RENAME_COLLECTION': 'Введите новое название коллекции.',
        'COLLECTION_RENAMED': 'Вы переименовали коллекцию «{}» в коллекцию «{}»'
    }

    COLLECTIONS_BUTTONS = {
        '+ Новая коллекция': 'create_collection',
        '‹ Назад': 'home'
    }

    COLLECTION_MENU = {
        'INTERFACE': '*Название:* {}\n*Ключ коллекции:* ```{}```\n*Карточек:* {}\n*Дата создания:* {}'
    }

    COLLECTION_BUTTONS = {
        'Продолжить изучение': 'collection_continue_{collection}',
        'Редактор карт': 'cards_{collection}_level_0',
        'Изменить название': 'collection_rename_{collection}',
        'Удалить коллекцию': 'collection_delete_{collection}',
        '« Личный кабинет': 'home',
        '‹ Назад': 'collections'
    }

    COLLECTION_CONTINUE_BUTTONS = {
        '✓ Показать описание': 'card_continue_{card}',
        '× Завершить обучение': 'collection_show_{collection}'
    }

    DELETE_COLLECTION = {
        'DELETE': 'Вы точно хотите удалить коллекцию?',
        'DELETE_SUCCESSFUL': 'Вы успешно удалили коллекцию «{}».',
        'DELETE_CANCELED': 'Удаление отменено.'
    }

    DELETE_COLLECTION_BUTTONS = {
        '✓ Да, удалить эту коллекцию.': 'collection_delete_yes_{collection}',
        '× Нет, это ошибка!': 'collection_delete_no_{collection}'
    }



    CARDS = {
        'INTERFACE': 'Карты коллекции «{}»:',
        'CARD_NAME': 'Введите название карточки.',
        'CARD_DESCRIPTION': 'Введите описание карточки.',
        'CARD_CREATED': 'Вы создали карточку «{}».',
        'RENAME_CARD': 'Введите новое название карточки.',
        'CARD_RENAMED': 'Вы переименовали карточку «{}» в карту «{}».',
        'EDIT_DESCRIPTION_CARD': 'Введите новое описание карточки.',
        'CARD_EDITED': 'Вы успешно изменили описание карточки.'
    }

    CARDS_BUTTONS = {
        '+ Новая карта': 'create_card_{collection}',
        '‹ Назад': 'collection_show_{collection}'
    }
    
    CARD_MENU = {
        'INTERFACE': '{}\n\n{}\n\n',
        'INFO_INTERFACE': '*Название:* {}\n*Описание:* {}\n*Дата создания:* {}\n*Рейтинг карты:* {}'
    }

    CARD_RESULT_BUTTONS = {
        'Отлично, запомнил (-а)!': 'card_result_{collection}_{card}_3',
        'Надо будет повторить!': 'card_result_{collection}_{card}_1',
        'Плохо помню эту карту!': 'card_result_{collection}_{card}_0'
    }

    CARD_ORIGINAL_MENU_BUTTONS = {
        'Изменить название': 'card_rename_{card}',
        'Изменить описание': 'card_description_{card}',
        'Показать информацию': 'card_on_info_{card}',
        'Удалить карту': 'card_delete_{card}',
        '« Личный кабинет': 'home',
        '‹ Назад': 'cards_{collection}_level_0'
    }

    CARD_INFO_MENU_BUTTONS = {
        'Изменить название': 'card_rename_{card}',
        'Изменить описание': 'card_description_{card}',
        'Скрыть информацию': 'card_off_info_{card}',
        'Удалить карту': 'card_delete_{card}',
        '« Личный кабинет': 'home',
        '‹ Назад': 'cards_{collection}_level_0'
    }

    DELETE_CARD = {
        'DELETE': 'Вы точно хотите удалить карту?',
        'DELETE_SUCCESSFUL': 'Вы успешно удалили карту «{}».',
        'DELETE_CANCELED': 'Удаление отменено.'
    }

    DELETE_CARD_BUTTONS = {
        '✓ Да, удалить эту карту.': 'card_delete_yes_{card}',
        '× Нет, это ошибка!': 'card_delete_no_{card}'
    }

    

    ERRORS = {
        0: 'Эта сессия устарела!',
        1: 'Ошибка создания коллекции! Вы находитесь в процессе создания коллекции. Завершите или отмените операцию.',
        2: 'Ошибка переименования коллекции! Вы находитесь в процессе переименования коллекции. Завершите или отмените операцию.',
        3: 'Коллекция с таким названием уже существует! Придумайте и введите другое название.',
        4: 'Ошибка создания карточки! Вы находитесь в процессе создания карточки. Завершите или отмените операцию.',
        5: 'Ошибка переименования карты! Вы находитесь в процессе переименования карточки. Завершите или отмените операцию.',
        6: 'Карта с таким названием уже существует! Придумайте и введите другое название.',
        7: 'Ошибка изменения описания карты! Вы находитесь в процессе изменения описания карточки. Завершите или отмените операцию.',
        8: 'В этой коллекции пока нет карт! Зайдите в меню «Редактор карт» и добавьте новую карточку.',
        9: 'У вас уже есть копия этой коллекции! Удалите копию коллекции или введите другой ключ.'
    }
