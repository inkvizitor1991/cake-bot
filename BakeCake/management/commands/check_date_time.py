import datetime


def check_date(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print('Введена не корректная дата.')
        return False
    return True


def check_time(time):
    try:
        datetime.datetime.strptime(time, '%H:%M')
    except ValueError:
        print('Введено некорректное время.')
        return False
    return True


def get_datetime(date, time='15:00'):
    if check_date(date) and check_time(time):
        date = date.split('-')
        time = time.split(':')
        delivery_date = date + time
        union_text = int(''.join(delivery_date))
        today = int(datetime.datetime.today().strftime(
            '%Y%m%d%H%M'))
        tomorrow = int(
            (datetime.datetime.today() + datetime.timedelta(days=1)).strftime(
                '%Y%m%d%H%M'))
        if union_text > tomorrow:
            return 'Красава'
        elif union_text in range(today, tomorrow):
            return 'С тебя +20% за скорость'
        else:
            return 'Не можем приготовить задним числом'



