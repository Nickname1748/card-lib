class Messages:
    ASSISTANCE = {
        'START' : 'Приветствие',
        'INSTRUCTIONS' : 'Инструкции',
        'HELP' : 'Помощь',
        'CANCEL' : 'Операция отменена!',
        'OLD_SESSION' : 'Эта сессия устарела!'
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
        '<  Назад' : 'home'
    }


    COLLECTIONS = {
        'INTERFACE' : 'Ваши коллекции.',
        'CREATE_COLLECTION' : 'Введите название коллекции.',
        'COLLECTION_CREATED' : 'Вы создали коллекцию «{}».'
    }

    COLLECTIONS_BUTTONS = {
        'Новая коллекция' : 'create_collection',
        '<  Назад' : 'home'
    }

    COLLECTION_MENU = {
        'INTERFACE' : 'Название: {}.\nКарточек: {}.\nДата создания: {}.'
    }

    COLLECTION_BUTTONS = {
        'Продолжить изучение' : 'cards_{}',
        'Добавить карточку' : 'new_card_{}',
        'Изменить название' : 'rename_{}',
        'Удалить коллекцию' : 'delete_{}',
        'Личный кабинет' : 'home',
        '<  Назад' : 'collections'
    }


    ERRORS = {
        1 : 'Ошибка создания коллекции! Вы находитесь в процессе создания коллекции. Завершите или отмените операцию.',
        2 : 'Ошибка переименования коллекции! Вы находитесь в процессе переименования коллекции. Завершите или отмените операцию.'
    }
