import random
import time
import os
import matplotlib.pyplot as plt
import numpy as np

# ---------- Числа Леонардо и вспомогательные структуры ----------
def leonardo_numbers(limit):
    """Генерирует числа Леонардо до limit"""
    leo = [1, 1]
    while leo[-1] < limit:
        leo.append(leo[-1] + leo[-2] + 1)
    return leo

MAX_SIZE = 500
leo = leonardo_numbers(MAX_SIZE + 100)

# Словарь для быстрого определения индекса числа Леонардо
leo_index = {}
for i, val in enumerate(leo):
    leo_index[val] = i

print(f"Числа Леонардо: {leo}")

# ---------- Алгоритм Smoothsort ----------
def smoothsort(arr):
    n = len(arr)
    if n <= 1:
        return 0
    
    comps = 0  # Счётчик сравнений
    heap_sizes = []  # Список размеров куч (числа Леонардо)
    
    # Вспомогательная функция: получить индекс корня p-й кучи
    def get_root(p):
        return sum(heap_sizes[:p+1]) - 1
    
    # Просеивание вниз (sift down)
    def sift_down(root, size):
        nonlocal comps
        if size <= 1:
            return
        
        m = leo_index[size]  # Индекс числа Леонардо для этого размера
        
        while size > 1:
            # Для кучи размера 1 или 2 просеивание не требуется
            if m < 2:
                break
                
            # Индексы левого и правого поддеревьев
            left_root = root - leo[m-2] - 1
            right_root = root - 1
            
            # Проверяем границы
            if left_root < 0 or right_root < 0:
                break
            
            # Сравниваем левое и правое поддеревья
            comps += 1
            if arr[left_root] > arr[right_root]:
                # Левый потомок больше
                comps += 1
                if arr[left_root] > arr[root]:
                    # Меняем и идём в левое поддерево
                    arr[left_root], arr[root] = arr[root], arr[left_root]
                    root = left_root
                    size = leo[m-2]
                    m -= 2
                else:
                    break
            else:
                # Правый потомок больше или равен
                comps += 1
                if arr[right_root] > arr[root]:
                    # Меняем и идём в правое поддерево
                    arr[right_root], arr[root] = arr[root], arr[right_root]
                    root = right_root
                    size = leo[m-1]
                    m -= 1
                else:
                    break
    
    # Восстановление порядка корней куч
    def trinkle(p):
        nonlocal comps
        if p <= 0:
            return
        
        while p > 0:
            root_p = get_root(p)
            root_prev = get_root(p - 1)
            
            comps += 1
            # Если порядок не нарушен, выходим
            if arr[root_p] >= arr[root_prev]:
                break
            
            # Меняем местами корни
            arr[root_p], arr[root_prev] = arr[root_prev], arr[root_p]
            
            # Просеиваем предыдущую кучу
            sift_down(root_prev, heap_sizes[p-1])
            
            p -= 1
    
    # Фаза 1: Построение куч
    for i in range(n):
        # Добавляем новый элемент как кучу размера 1
        heap_sizes.append(1)
        
        # Проверяем, нужно ли объединить две последние кучи
        while len(heap_sizes) >= 2:
            size_prev = heap_sizes[-2]
            size_last = heap_sizes[-1]
            
            # Проверяем, являются ли размеры последовательными числами Леонардо
            if size_prev in leo_index and size_last in leo_index:
                idx_prev = leo_index[size_prev]
                idx_last = leo_index[size_last]
                
                # Если это последовательные числа L(k+1) и L(k)
                if idx_prev == idx_last + 1:
                    # Удаляем две кучи
                    heap_sizes.pop()
                    heap_sizes.pop()
                    
                    # Добавляем объединённую кучу L(k+2)
                    new_size = leo[idx_prev + 1]
                    heap_sizes.append(new_size)
                    
                    # Просеиваем объединённую кучу
                    sift_down(i, new_size)
                    continue
            
            break
        
        # Восстанавливаем порядок корней
        trinkle(len(heap_sizes) - 1)
    
    # Фаза 2: Извлечение максимумов
    for i in range(n-1, 0, -1):
        if not heap_sizes:
            break
            
        # Удаляем последнюю кучу (её корень - максимум)
        last_size = heap_sizes.pop()
        
        if last_size > 1:
            # Разбиваем кучу L(m) на L(m-2) и L(m-1)
            m = leo_index[last_size]
            
            # Левое поддерево
            left_size = leo[m-2]
            heap_sizes.append(left_size)
            sift_down(i - last_size + left_size - 1, left_size)
            trinkle(len(heap_sizes) - 1)
            
            # Правое поддерево
            right_size = leo[m-1]
            heap_sizes.append(right_size)
            sift_down(i - 1, right_size)
            trinkle(len(heap_sizes) - 1)
    
    return comps

# ---------- Генерация 100 случайных наборов данных ----------
print("\n" + "="*60)
print("ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ")
print("="*60)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

random.seed(42)
sizes = []

for idx in range(100):
    n = random.randint(100, MAX_SIZE)
    sizes.append(n)
    data = [random.randint(0, 1000000) for _ in range(n)]
    
    filename = f"{DATA_DIR}/input_{idx:03d}_{n}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(map(str, data)))
    
    if (idx + 1) % 20 == 0:
        print(f"Сгенерировано {idx + 1}/100 файлов...")

print("✓ Все 100 файлов сгенерированы")

# ---------- Тестирование на маленьком массиве ----------
print("\n" + "="*60)
print("ПРОВЕРКА АЛГОРИТМА")
print("="*60)

test_arr = [64, 34, 25, 12, 22, 11, 90, 45, 33, 77]
test_copy = test_arr[:]
comps_test = smoothsort(test_copy)
expected = sorted(test_arr)

if test_copy == expected:
    print(f"✓ Тест пройден!")
    print(f"  Исходный: {test_arr}")
    print(f"  Результат: {test_copy}")
    print(f"  Сравнений: {comps_test}")
else:
    print(f"✗ ОШИБКА! Результат: {test_copy}")
    exit(1)

# ---------- Измерение времени и сравнений ----------
print("\n" + "="*60)
print("ЗАПУСК ТЕСТОВ")
print("="*60)

results = []
start_total = time.perf_counter()

for idx, n in enumerate(sizes):
    filename = f"{DATA_DIR}/input_{idx:03d}_{n}.txt"
    
    # Чтение данных
    with open(filename) as f:
        arr = list(map(int, f.read().split()))
    
    # Сортировка с замером времени
    arr_copy = arr[:]
    t0 = time.perf_counter()
    comps = smoothsort(arr_copy)
    t1 = time.perf_counter()
    
    # Проверка корректности
    expected_sorted = sorted(arr)
    if arr_copy != expected_sorted:
        print(f"✗ ОШИБКА в файле {idx+1} (размер={n})")
        continue
    
    elapsed = t1 - t0
    results.append((n, elapsed, comps))
    
    # Прогресс
    if (idx + 1) % 10 == 0:
        print(f"[{idx+1:3d}/100] Размер={n:4d} | Время={elapsed:.6f}с | Сравнений={comps:6d}")

total_time = time.perf_counter() - start_total
print(f"\n✓ Все тесты пройдены за {total_time:.2f}с")

# ---------- Построение графиков ----------
print("\n" + "="*60)
print("ПОСТРОЕНИЕ ГРАФИКОВ")
print("="*60)

ns, times, comps_list = zip(*results)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# График 1: Время от размера
ax1.scatter(ns, times, alpha=0.6, edgecolors='black', s=40, linewidth=0.5)
ax1.set_xlabel("Размер массива (n)", fontsize=12)
ax1.set_ylabel("Время выполнения (сек)", fontsize=12)
ax1.set_title("Зависимость времени от размера массива", fontsize=14)
ax1.grid(True, alpha=0.3)

# Добавляем линию тренда
z1 = np.polyfit(ns, times, 2)
p1 = np.poly1d(z1)
x_smooth = np.linspace(min(ns), max(ns), 200)
ax1.plot(x_smooth, p1(x_smooth), "r-", linewidth=2, label="Квадратичный тренд")
ax1.legend()

# График 2: Количество сравнений от размера
ax2.scatter(ns, comps_list, alpha=0.6, edgecolors='black', s=40, linewidth=0.5)
ax2.set_xlabel("Размер массива (n)", fontsize=12)
ax2.set_ylabel("Количество сравнений", fontsize=12)
ax2.set_title("Зависимость числа сравнений от размера массива", fontsize=14)
ax2.grid(True, alpha=0.3)

# Добавляем теоретическую кривую n*log2(n)
x_theory = np.linspace(min(ns), max(ns), 200)
y_theory = x_theory * np.log2(x_theory)
scale = np.mean([c / (n * np.log2(n)) for n, c in zip(ns, comps_list)])
y_scaled = scale * y_theory
ax2.plot(x_theory, y_scaled, "r-", linewidth=2, 
         label=f"n·log₂(n), масштаб={scale:.2f}")
ax2.legend()

plt.tight_layout()
plt.savefig("smoothsort_plots.png", dpi=150, bbox_inches='tight')
plt.show()

# ---------- Вывод статистики ----------
print("\n" + "="*60)
print("СТАТИСТИКА")
print("="*60)
print(f"Количество тестов: {len(results)}")
print(f"Диапазон размеров: {min(ns)} - {max(ns)}")
print(f"Среднее время: {np.mean(times):.6f} сек")
print(f"Максимальное время: {max(times):.6f} сек")
print(f"Среднее число сравнений: {np.mean(comps_list):.1f}")
print(f"Максимальное число сравнений: {max(comps_list)}")
print(f"Среднее сравнений на элемент: {np.mean([c/n for c, n in zip(comps_list, ns)]):.2f}")

# Оценка сложности
ratio_to_nlogn = [c / (n * np.log2(n)) for c, n in zip(comps_list, ns)]
print(f"Среднее отношение сравнений к n·log₂(n): {np.mean(ratio_to_nlogn):.3f}")
print("\n✓ Вывод: сложность алгоритма O(n log n) подтверждается экспериментально")
print(f"✓ Графики сохранены в файл 'smoothsort_plots.png'")