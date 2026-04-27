class IntSet:
    # Множество целых чисел на основе хеш-таблицы с цепочками

    def __init__(self, initial_capacity=8, load_factor=0.75):
        # Конструктор. Создает пустую хеш-таблицу
        self._capacity = initial_capacity
        self._load_factor = load_factor
        self._size = 0
        # _buckets: список цепочек, каждая цепочка - список чисел
        self._buckets = [[] for _ in range(self._capacity)]

    def _hash(self, value):
        # Хеш-функция для целого числа
        return abs(value) % self._capacity

    def _should_rehash(self):
        # Проверяет, нужно ли расширять таблицу
        return self._size / self._capacity >= self._load_factor

    def add(self, value):
        # Добавить число. Если уже есть, ничего не менять
        if not isinstance(value, int):
            raise TypeError("IntSet хранит только целые числа")
        index = self._hash(value)
        bucket = self._buckets[index]
        if value not in bucket:
            bucket.append(value)
            self._size += 1
            if self._should_rehash():
                self.rehash()

    def remove(self, value):
        # Удалить число. Если нет, ничего не менять
        if not isinstance(value, int):
            raise TypeError("IntSet хранит только целые числа")
        index = self._hash(value)
        bucket = self._buckets[index]
        if value in bucket:
            bucket.remove(value)
            self._size -= 1

    def contains(self, value):
        # Проверить наличие числа. Возвращает bool
        if not isinstance(value, int):
            return False
        index = self._hash(value)
        bucket = self._buckets[index]
        return value in bucket

    def size(self):
        # Количество элементов
        return self._size

    def clear(self):
        # Удалить все элементы
        self._capacity = 8
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]

    def rehash(self):
        # Увеличить внутреннюю таблицу и перераспределить элементы
        old_buckets = self._buckets
        self._capacity *= 2
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]
        for bucket in old_buckets:
            for value in bucket:
                self.add(value)

    def __str__(self):
        # Строковое представление для удобства отладки
        elements = []
        for bucket in self._buckets:
            elements.extend(bucket)
        return "{" + ", ".join(str(e) for e in elements) + "}"


# Точка входа с демонстрацией всех методов
if __name__ == "__main__":
    print("=== Демонстрация IntSet ===")
    s = IntSet()
    
    print("\n1. add()")
    s.add(5)
    s.add(7)
    s.add(5)  # дубликат, не добавится
    print(f"После добавления 5, 7, 5: {s}")
    
    print("\n2. contains()")
    print(f"contains(7) = {s.contains(7)}")
    print(f"contains(3) = {s.contains(3)}")
    
    print("\n3. size()")
    print(f"Размер: {s.size()}")
    
    print("\n4. remove()")
    s.remove(7)
    s.remove(10)  # нет в множестве
    print(f"После удаления 7 и 10: {s}")
    print(f"Размер: {s.size()}")
    
    print("\n5. rehash()")
    for i in range(20):
        s.add(i)
    print(f"После добавления 20 элементов: размер={s.size()}, capacity={s._capacity}")
    
    print("\n6. clear()")
    s.clear()
    print(f"После clear(): {s}, размер={s.size()}")


# ============ ТЕСТЫ ============
import unittest


class TestIntSet(unittest.TestCase):

    def setUp(self):
        # Конструктор тестируется неявно через setUp
        self.int_set = IntSet()

    # --- add ---
    def test_add_new_element(self):
        s = IntSet()
        s.add(10)
        self.assertTrue(s.contains(10))
        self.assertEqual(s.size(), 1)

    def test_add_duplicate(self):
        s = IntSet()
        s.add(10)
        s.add(10)
        self.assertEqual(s.size(), 1)

    def test_add_negative(self):
        s = IntSet()
        s.add(-5)
        self.assertTrue(s.contains(-5))

    def test_add_triggers_rehash(self):
        s = IntSet(initial_capacity=4, load_factor=0.6)
        s.add(1)
        s.add(2)  # 2/4 = 0.5 < 0.6 -> без rehash
        self.assertEqual(s._capacity, 4)
        s.add(3)  # 3/4 = 0.75 >= 0.6 -> rehash
        self.assertEqual(s._capacity, 8)

    def test_add_invalid_type(self):
        s = IntSet()
        with self.assertRaises(TypeError):
            s.add("строка")

    # --- remove ---
    def test_remove_existing(self):
        s = IntSet()
        s.add(10)
        s.remove(10)
        self.assertFalse(s.contains(10))
        self.assertEqual(s.size(), 0)

    def test_remove_non_existing(self):
        s = IntSet()
        s.add(10)
        s.remove(20)
        self.assertEqual(s.size(), 1)

    def test_remove_from_bucket_with_collision(self):
        s = IntSet(initial_capacity=4)
        # Добавляем значения с одинаковым хешем
        s.add(0)
        s.add(4)  # хеш 0 при capacity=4
        s.remove(0)
        self.assertFalse(s.contains(0))
        self.assertTrue(s.contains(4))

    def test_remove_invalid_type(self):
        s = IntSet()
        with self.assertRaises(TypeError):
            s.remove("строка")

    # --- contains ---
    def test_contains_true(self):
        s = IntSet()
        s.add(42)
        self.assertTrue(s.contains(42))

    def test_contains_false(self):
        s = IntSet()
        self.assertFalse(s.contains(99))

    def test_contains_negative(self):
        s = IntSet()
        s.add(-1)
        self.assertTrue(s.contains(-1))
        self.assertFalse(s.contains(1))

    def test_contains_invalid_type(self):
        s = IntSet()
        self.assertFalse(s.contains("строка"))

    # --- size ---
    def test_size_empty(self):
        self.assertEqual(self.int_set.size(), 0)

    def test_size_after_operations(self):
        s = IntSet()
        s.add(1)
        s.add(2)
        s.add(2)
        s.remove(1)
        self.assertEqual(s.size(), 1)

    def test_size_after_clear(self):
        s = IntSet()
        s.add(1)
        s.clear()
        self.assertEqual(s.size(), 0)

    # --- clear ---
    def test_clear_removes_all(self):
        s = IntSet()
        s.add(1)
        s.add(2)
        s.clear()
        self.assertEqual(s.size(), 0)
        self.assertFalse(s.contains(1))

    def test_clear_resets_capacity(self):
        s = IntSet()
        s.add(1)
        s.rehash()  # увеличиваем capacity
        old_cap = s._capacity
        s.clear()
        self.assertEqual(s._capacity, 8)
        self.assertLess(s._capacity, old_cap)

    # --- rehash ---
    def test_rehash_doubles_capacity(self):
        s = IntSet()
        old_cap = s._capacity
        s.rehash()
        self.assertEqual(s._capacity, old_cap * 2)

    def test_rehash_preserves_elements(self):
        s = IntSet()
        elements = [5, 10, 15, 20]
        for e in elements:
            s.add(e)
        s.rehash()
        for e in elements:
            self.assertTrue(s.contains(e))
        self.assertEqual(s.size(), len(elements))

    def test_rehash_handles_collisions(self):
        s = IntSet(initial_capacity=2)
        s.add(0)
        s.add(2)  # коллизия: хеш 0
        s.add(1)
        s.add(3)  # коллизия: хеш 1
        s.rehash()
        self.assertTrue(s.contains(0))
        self.assertTrue(s.contains(2))
        self.assertTrue(s.contains(1))
        self.assertTrue(s.contains(3))
        self.assertEqual(s.size(), 4)


if __name__ == "__main__":
    unittest.main()