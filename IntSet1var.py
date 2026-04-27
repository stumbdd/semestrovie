class Node:
    """Узел односвязного списка для цепочек хеш-таблицы."""
    __slots__ = ('value', 'next')

    def __init__(self, value: int, next_node: 'Node' = None):
        self.value = value
        self.next = next_node


class IntSet:
    """Множество целых чисел на базе хеш-таблицы с цепочками."""

    def __init__(self, initial_capacity: int = 8, load_factor: float = 0.75):
        if initial_capacity < 1:
            raise ValueError("Capacity must be > 0")
        self._capacity = initial_capacity
        self._size = 0
        self._load_factor = load_factor
        # Массив бакетов: каждый элемент либо None, либо голова связного списка
        self._buckets = [None] * self._capacity

    def _hash_index(self, value: int) -> int:
        """Вычисляет индекс корзины для значения."""
        return value % self._capacity

    def add(self, value: int) -> None:
        """Добавляет число в множество. Если уже есть — ничего не делает."""
        idx = self._hash_index(value)
        current = self._buckets[idx]

        # Проверяем, есть ли уже такое значение в цепочке
        while current is not None:
            if current.value == value:
                return  # уже существует, ничего не делаем
            current = current.next

        # Добавляем новый узел в начало цепочки
        new_node = Node(value, self._buckets[idx])
        self._buckets[idx] = new_node
        self._size += 1

        # Проверяем коэффициент заполнения
        if self._size / self._capacity > self._load_factor:
            self.rehash()

    def remove(self, value: int) -> None:
        """Удаляет число из множества. Если отсутствует — ничего не делает."""
        idx = self._hash_index(value)
        current = self._buckets[idx]
        prev = None

        while current is not None:
            if current.value == value:
                if prev is None:
                    # Удаляем голову цепочки
                    self._buckets[idx] = current.next
                else:
                    prev.next = current.next
                self._size -= 1
                return
            prev = current
            current = current.next

    def contains(self, value: int) -> bool:
        """Проверяет, содержится ли число в множестве."""
        idx = self._hash_index(value)
        current = self._buckets[idx]
        while current is not None:
            if current.value == value:
                return True
            current = current.next
        return False

    def size(self) -> int:
        """Возвращает количество элементов в множестве."""
        return self._size

    def clear(self) -> None:
        """Удаляет все элементы, сохраняя текущую ёмкость таблицы."""
        self._buckets = [None] * self._capacity
        self._size = 0

    def rehash(self) -> None:
        """Увеличивает размер внутренней таблицы вдвое и перераспределяет элементы."""
        new_capacity = self._capacity * 2
        new_buckets = [None] * new_capacity

        # Обходим все цепочки старой таблицы
        for head in self._buckets:
            current = head
            while current is not None:
                # Сохраняем следующий узел, чтобы не потерять при переносе
                nxt = current.next
                # Вставляем в новую таблицу в начало цепочки
                new_idx = current.value % new_capacity
                current.next = new_buckets[new_idx]
                new_buckets[new_idx] = current
                current = nxt

        self._buckets = new_buckets
        self._capacity = new_capacity


# Тесты

def test_add():
    s = IntSet(4, 0.75)  # маленький размер для проверки рехеширования
    s.add(5)
    assert s.size() == 1
    assert s.contains(5) == True

    s.add(7)
    assert s.size() == 2
    assert s.contains(7) == True

    # Дубликат
    s.add(5)
    assert s.size() == 2  # размер не изменился
    assert s.contains(5) == True

    # Добавление отрицательного
    s.add(-3)
    assert s.contains(-3) == True
    assert s.size() == 3

    print("test_add passed")


def test_remove():
    s = IntSet()
    s.add(10)
    s.add(20)
    s.add(30)
    s.remove(20)
    assert s.size() == 2
    assert s.contains(20) == False
    assert s.contains(10) == True
    assert s.contains(30) == True

    # Удаление несуществующего
    s.remove(100)
    assert s.size() == 2

    # Удаление из пустой цепочки
    s.clear()
    s.remove(5)  # не должно быть ошибок
    assert s.size() == 0

    # Удаление головы цепочки
    s.add(1)
    s.add(2)
    s.remove(1)
    assert s.contains(1) == False
    assert s.size() == 1

    # Удаление последнего элемента
    s.remove(2)
    assert s.size() == 0

    print("test_remove passed")


def test_contains():
    s = IntSet()
    assert s.contains(42) == False
    s.add(42)
    assert s.contains(42) == True
    s.remove(42)
    assert s.contains(42) == False

    # Проверка на коллизиях (один бакет)
    s2 = IntSet(1)  # все элементы в одну корзину из-за деления по модулю 1? capacity=1 => все индексы 0
    # Но capacity=1, индекс будет всегда 0, коллизии разрешаются цепочкой
    s2.add(100)
    s2.add(200)
    assert s2.contains(100) == True
    assert s2.contains(200) == True
    assert s2.contains(300) == False

    print("test_contains passed")


def test_size():
    s = IntSet()
    assert s.size() == 0
    s.add(1)
    assert s.size() == 1
    s.add(2)
    s.add(3)
    assert s.size() == 3
    s.remove(2)
    assert s.size() == 2
    s.clear()
    assert s.size() == 0

    print("test_size passed")


def test_clear():
    s = IntSet()
    s.add(1)
    s.add(2)
    s.add(3)
    s.clear()
    assert s.size() == 0
    assert s.contains(1) == False
    assert s.contains(2) == False
    assert s.contains(3) == False

    # Проверка, что после clear можно снова добавлять
    s.add(4)
    assert s.size() == 1
    assert s.contains(4) == True

    # clear пустого множества
    s.clear()
    s.clear()
    assert s.size() == 0

    print("test_clear passed")


def test_rehash():
    s = IntSet(4, 0.75)  # capacity=4, threshold=3
    # Добавляем элементы, чтобы вызвать автоматический rehash
    s.add(1)
    s.add(2)
    s.add(3)  # 3/4 = 0.75, не превышает (превышение > 0.75), поэтому rehash не вызывается
    assert s._capacity == 4
    s.add(4)  # 4/4 = 1.0 > 0.75 => должен быть rehash
    assert s._capacity == 8  # удвоение
    assert s.size() == 4
    # Проверяем наличие всех элементов
    for val in [1, 2, 3, 4]:
        assert s.contains(val) == True

    # Ручной вызов rehash при нескольких элементах
    s2 = IntSet(2, 0.75)
    s2.add(10)
    s2.add(20)  # 2/2 = 1.0 > 0.75 => rehash до 4
    assert s2._capacity == 4
    s2.rehash()  # явный вызов, capacity станет 8
    assert s2._capacity == 8
    assert s2.contains(10) == True
    assert s2.contains(20) == True
    assert s2.size() == 2

    print("test_rehash passed")


def run_tests():
    test_add()
    test_remove()
    test_contains()
    test_size()
    test_clear()
    test_rehash()
    print("All tests passed!\n")



# Демонстрация в main

def main():
    # Показываем создание и базовые операции
    print("=== IntSet Demonstration ===")
    s = IntSet()
    print(f"New set, size: {s.size()}")

    s.add(5)
    s.add(7)
    s.add(5)  # дубликат
    print(f"Added 5, 7, 5. Size: {s.size()}")
    print(f"contains(7): {s.contains(7)}")
    print(f"contains(3): {s.contains(3)}")

    s.remove(7)
    print(f"After remove(7): size={s.size()}, contains(7)={s.contains(7)}")

    s.clear()
    print(f"After clear: size={s.size()}")

    # Демонстрация rehash с маленьким начальным размером
    print("\n--- Rehash demonstration ---")
    s2 = IntSet(2, 0.75)   # ёмкость 2, порог 0.75
    print(f"Initial capacity: {s2._capacity}")
    values = [1, 2, 3]
    for v in values:
        s2.add(v)
        print(f"Added {v}, size={s2.size()}, capacity={s2._capacity}")

    print(f"Contains all?: {all(s2.contains(v) for v in values)}")

    # Явный rehash (удвоение ёмкости)
    s2.rehash()
    print(f"After manual rehash: capacity={s2._capacity}, size={s2.size()}")
    print(f"Contains all?: {all(s2.contains(v) for v in values)}")

    # Покажем работу с отрицательными числами
    print("\n--- Negative numbers ---")
    s3 = IntSet()
    s3.add(-10)
    s3.add(0)
    s3.add(-10)
    print(f"Size: {s3.size()}, contains(-10): {s3.contains(-10)}, contains(0): {s3.contains(0)}")
    s3.remove(-10)
    print(f"After remove(-10): size={s3.size()}, contains(-10)={s3.contains(-10)}")

if __name__ == "__main__":
    run_tests()
    main()