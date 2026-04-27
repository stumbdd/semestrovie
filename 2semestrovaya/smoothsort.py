import random
import os
import time
import copy

# ==========================================
# Генерация тестовых данных (500-1000 элементов)
# ==========================================

def generate_datasets(num_sets=100, min_size=500, max_size=1000):
    # Генерирует файлы с массивами случайных чисел
    if not os.path.exists("datasets"):
        os.makedirs("datasets")
    
    sizes = []
    for i in range(num_sets):
        size = random.randint(min_size, max_size)
        sizes.append(size)
        arr = [random.randint(-100000, 100000) for _ in range(size)]
        filename = f"datasets/dataset_{i+1:03d}.txt"
        with open(filename, "w") as f:
            f.write(str(size) + "\n")
            f.write(" ".join(map(str, arr)))
    return sizes


def load_dataset(filename):
    # Читает массив из файла, возвращает размер и список
    with open(filename, "r") as f:
        size = int(f.readline().strip())
        arr = list(map(int, f.readline().strip().split()))
    return size, arr


# ==========================================
# Числа Леонардо для SmoothSort
# ==========================================

def leonardo_numbers(limit):
    # Генерирует числа Леонардо: L(0)=1, L(1)=1, L(k)=L(k-1)+L(k-2)+1
    nums = [1, 1]
    while nums[-1] <= limit:
        nums.append(nums[-1] + nums[-2] + 1)
    return nums


# ==========================================
# SmoothSort с подсчётом шагов
# ==========================================

class SmoothSortStats:
    # Контейнер для хранения счётчиков операций
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
    
    def total_steps(self):
        return self.comparisons + self.swaps


def smooth_sort(arr, stats):
    # SmoothSort на месте, stats хранит количество сравнений и обменов
    if len(arr) <= 1:
        return
    
    # Числа Леонардо до длины массива, делаем глобальным списком для функций
    global leo
    leo = leonardo_numbers(len(arr))
    
    # Размеры куч в структуре
    heap_sizes = []
    
    # --- Фаза 1: построение леса куч Леонардо ---
    for i in range(len(arr)):
        # Проверяем, можно ли слить две последние кучи с новым элементом
        if len(heap_sizes) >= 2 and heap_sizes[-1] == heap_sizes[-2] + 1:
            # Сливаем: убираем две последние, увеличиваем предпоследнюю
            heap_sizes.pop()
            heap_sizes[-1] += 1
        else:
            # Добавляем кучу размера 1
            if len(heap_sizes) >= 1 and heap_sizes[-1] == 1:
                # Рядом с кучей размера 1 добавляется куча размера 0 (заглушка)
                heap_sizes.append(0)
            else:
                heap_sizes.append(1)
        
        # Восстанавливаем свойства кучи просеиванием вверх
        restore_heaps(arr, i, heap_sizes, stats)
    
    # --- Фаза 2: извлечение максимумов ---
    for i in range(len(arr) - 1, 0, -1):
        if len(heap_sizes) == 0:
            break
        
        # Последняя куча отдаёт свой корень (максимум)
        last_heap_size = heap_sizes.pop()
        
        if last_heap_size > 1:
            # Разбиваем кучу на две меньшие
            left_child_end = i - leo[last_heap_size - 2] - 1
            right_child_end = i - 1
            
            heap_sizes.append(last_heap_size - 1)
            heap_sizes.append(last_heap_size - 2)
            
            # Просеиваем корни обеих дочерних куч
            restore_heaps(arr, left_child_end, heap_sizes, stats)
            restore_heaps(arr, right_child_end, heap_sizes, stats)
        # Если last_heap_size <= 1, то куча из одного элемента, 
        # ничего не делаем (элемент уже на месте)
        # Кучу размера 0 просто пропускаем


def restore_heaps(arr, idx, heap_sizes, stats):
    # Просеивание вниз для восстановления свойства max-heap
    # current указывает на конец кучи в массиве
    current = idx
    # heap_sizes описывает лес, последний элемент — размер текущей кучи
    # но мы работаем только с последней кучей
    
    while len(heap_sizes) > 0:
        heap_idx = len(heap_sizes) - 1
        current_size = heap_sizes[heap_idx]
        
        # Кучи размера 0 и 1 не нужно просеивать
        if current_size <= 1:
            break
        
        # Вычисляем индексы детей
        # Левое поддерево имеет размер L(current_size - 1)
        # Правое поддерево имеет размер L(current_size - 2)
        right_child = current - 1
        left_child = current - 1 - leo[current_size - 2]
        
        # Ищем максимум среди корня и детей
        stats.comparisons += 1
        if left_child >= 0 and arr[left_child] > arr[current]:
            largest = left_child
        else:
            largest = current
        
        if right_child >= 0:
            stats.comparisons += 1
            if arr[right_child] > arr[largest]:
                largest = right_child
        
        # Если корень не максимальный — меняем и идём вниз
        if largest != current:
            stats.swaps += 1
            arr[current], arr[largest] = arr[largest], arr[current]
            
            # Определяем, в какое поддерево провалились
            if largest == left_child:
                # Уходим в левое поддерево
                # Заменяем текущую кучу на две: L(size-1) и L(size-2)
                heap_sizes.pop()  # убираем текущую кучу
                heap_sizes.append(current_size - 1)
                heap_sizes.append(current_size - 2)
                current = left_child
            else:
                # Уходим в правое поддерево
                heap_sizes.pop()
                heap_sizes.append(current_size - 2)
                heap_sizes.append(current_size - 3)
                current = right_child
        else:
            # Свойство кучи восстановлено
            break


# ==========================================
# Обёртка для замера времени
# ==========================================

def smooth_sort_timed(arr):
    # Возвращает кортеж: (отсортированный_массив, время_мс, количество_шагов)
    working_copy = copy.deepcopy(arr)
    stats = SmoothSortStats()
    
    start_time = time.perf_counter()
    smooth_sort(working_copy, stats)
    end_time = time.perf_counter()
    
    elapsed_ms = (end_time - start_time) * 1000
    return working_copy, elapsed_ms, stats.total_steps()


# ==========================================
# Проверка корректности
# ==========================================

def verify_sort(original, sorted_arr):
    # Проверяет, что sorted_arr является отсортированной версией original
    expected = sorted(original)
    return sorted_arr == expected


# ==========================================
# Основной блок измерений
# ==========================================

if __name__ == "__main__":
    print("Генерация 100 наборов данных (500-1000 элементов)...")
    sizes = generate_datasets(100, 500, 1000)
    print("Генерация завершена.\n")
    
    results = []  # список кортежей: (size, time_ms, steps)
    
    print("Запуск SmoothSort на каждом наборе...")
    for i in range(1, 101):
        filename = f"datasets/dataset_{i:03d}.txt"
        size, arr = load_dataset(filename)
        
        sorted_arr, elapsed, steps = smooth_sort_timed(arr)
        
        results.append((size, elapsed, steps))
        
        if i % 10 == 0:
            print(f"  Обработано {i}/100 наборов...")
    
    print("Измерения завершены.\n")
    
    # --- Вывод результатов ---
    print("=" * 60)
    print(f"{'Размер':<8}{'Время (мс)':<14}{'Шагов':<12}")
    print("-" * 60)
    for size, elapsed, steps in results:
        print(f"{size:<8}{elapsed:<14.4f}{steps:<12}")
    
    # --- Сохранение для графиков ---
    with open("results.txt", "w") as f:
        f.write("Size,Time_ms,Steps\n")
        for size, elapsed, steps in results:
            f.write(f"{size},{elapsed},{steps}\n")
    
    print("\nРезультаты сохранены в results.txt")


# ------ Графики ------

import matplotlib.pyplot as plt

# Читаем results.txt
sizes = []
times = []
steps_list = []

with open("results.txt", "r") as f:
    next(f)  # пропускаем заголовок
    for line in f:
        size, t, s = line.strip().split(",")
        sizes.append(int(size))
        times.append(float(t))
        steps_list.append(int(s))

# График 1: время от размера
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.scatter(sizes, times, alpha=0.6, color="blue", s=10)
plt.xlabel("Размер массива")
plt.ylabel("Время (мс)")
plt.title("Время выполнения SmoothSort")
plt.grid(True, alpha=0.3)

# График 2: количество шагов от размера
plt.subplot(1, 2, 2)
plt.scatter(sizes, steps_list, alpha=0.6, color="red", s=10)
plt.xlabel("Размер массива")
plt.ylabel("Количество шагов")
plt.title("Количество шагов SmoothSort")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("smoothsort_plots.png", dpi=150)
plt.show()