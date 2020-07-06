class Messages:
    ASSISTANCE = {
        'START' : 'Приветствие',
        'INSTRUCTIONS' : 'Инструкции',
        'HELP' : 'Помощь',
        'CANCEL' : 'Операция отменена!'
    }


    PRIVATE_OFFICE = {
        'INTERFACE' : 'Личный кабинет',
    }
    
    PRIVATE_OFFICE_BUTTONS = {
        'Профиль' : 'profile',
        'Коллекции' : 'collections'
    }


    PROFILE = {
        'INTERFACE' : 'Пользователь: @{}.\nКоллекций: {}.\nКарт: {}.'
    }

    PROFILE_BUTTONS = {
        '‹ Назад' : 'home'
    }


    COLLECTIONS = {
        'INTERFACE' : 'Ваши коллекции.',
        'CREATE_COLLECTION' : 'Введите название коллекции.',
        'COLLECTION_CREATED' : 'Вы создали коллекцию «{}».',
        'RENAME_COLLECTION' : 'Введите новое название коллекции.',
        'COLLECTION_RENAMED' : 'Вы переименовали коллекцию «{}» в коллекцию «{}»'
    }

    COLLECTIONS_BUTTONS = {
        '+ Новая коллекция' : 'create_collection',
        '‹ Назад' : 'home'
    }

    COLLECTION_MENU = {
        'INTERFACE' : 'Название: {}.\nКарточек: {}.\nДата создания: {}.'
    }

    COLLECTION_BUTTONS = {
        '~ Продолжить изучение' : 'collection_continue_{}',
        '# Редактор карт' : 'show_cards_{}',
        '* Изменить название' : 'collection_rename_{}',
        '– Удалить коллекцию' : 'collection_delete_{}',
        '« Личный кабинет' : 'home',
        '‹ Назад' : 'collections'
    }

    DELETE_COLLECTION = {
        'DELETE' : 'Вы точно хотите удалить коллекцию?',
        'DELETE_SUCCESSFUL' : 'Вы успешно удалили коллекцию «{}».',
        'DELETE_CANCELED' : 'Удаление отменено.'
    }

    DELETE_COLLECTION_BUTTONS = {
        '✓ Да, удалить эту коллекцию.' : 'collection_delete_yes_{}',
        '× Нет, это ошибка!' : 'collection_delete_no_{}'
    }


    ERRORS = {
        1 : 'Ошибка создания коллекции! Вы находитесь в процессе создания коллекции. Завершите или отмените операцию.',
        2 : 'Ошибка переименования коллекции! Вы находитесь в процессе переименования коллекции. Завершите или отмените операцию.',
        3 : 'Эта сессия устарела!',
        4 : 'Коллекция с таким названием уже существует! Придумайте и введите другое название.'
    }
