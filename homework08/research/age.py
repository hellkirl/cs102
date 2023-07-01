import datetime as dt
import statistics
import typing as tp

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    items = get_friends(user_id, fields=["bdate"]).items
    today = dt.datetime.now()
    year = today.year
    age = []
    for element in items:
        if "bdate" in element and len(element["bdate"]) >= 9:  # type: ignore
            birthdate_ = element["bdate"]  # type: ignore
            birth_year = int(birthdate_[-4:])
            age.append(year - birth_year)
    average_ = statistics.median(age) if age else None
    return average_


if __name__ == "__main__":
    print(age_predict(183238121))
