# -*- coding: utf-8 -*-
"""GA for hypperparam

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IvBH9BAKnIIW5R-WO-uY7NOrsMvWMK5M

**Навигация по уроку**
1. [Генетический алгоритм. Термины и понятия](https://colab.research.google.com/drive/14VjROMnDAiXvyv2nf47h16jJHJfM1Flm)
2. [Применение генетических алгоритмов](https://colab.research.google.com/drive/1lONPg4nYhkAcPkylT4unfJ2XFHBfyNhJ)
3. Домашняя работа

В домашней работе вам необходимо выполнить любую задачу на выбор:

# Установка библиотек
"""

#pip install deap

"""# Импорт библиотек"""

# Работа с массивами и данными
import numpy as np
import random  # Для случайных чисел
import time  # Для замера времени

# Метрики и подготовка данных
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

# Для генетического алгоритма
#from deap import base, creator, tools, algorithms

# Работа с машинным обучением
from keras.models import Sequential
from keras.layers import Dense, Input, Dropout
from keras import layers
from keras import optimizers
from keras.applications import VGG16

# Набор утилит для работы с файловой системой
import shutil
from tensorflow.keras.preprocessing.image import ImageDataGenerator

"""# Датасет"""

conv_base = VGG16(weights='imagenet', include_top=False, input_shape=(150, 150, 3))

# @title Загрузка набора данных

!wget https://storage.yandexcloud.net/academy.ai/cat-and-dog.zip
# Разархивируем датасета во временную папку 'temp'
!unzip -qo "cat-and-dog" -d ./temp

# @title Создание путей для датасета

# Папка с папками картинок, рассортированных по категориям
IMAGE_PATH = './temp/training_set/training_set/'

# Папка в которой будем создавать выборки
BASE_DIR = './dataset/'

# Определение списка имен классов
CLASS_LIST = sorted(os.listdir(IMAGE_PATH))

# Определение количества классов
CLASS_COUNT = len(CLASS_LIST)

# При повторном запуске пересоздаим структуру каталогов
# Если папка существует, то удаляем ее со всеми вложенными каталогами и файлами
if os.path.exists(BASE_DIR):
    shutil.rmtree(BASE_DIR)

# Создаем папку по пути BASE_DIR
os.mkdir(BASE_DIR)

# Сцепляем путь до папки с именем вложенной папки. Аналогично BASE_DIR + '/train'
train_dir = os.path.join(BASE_DIR, 'train')

# Создаем подпапку, используя путь
os.mkdir(train_dir)

# Сцепляем путь до папки с именем вложенной папки. Аналогично BASE_DIR + '/validation'
test_dir = os.path.join(BASE_DIR, 'test')

# Создаем подпапку, используя путь
os.mkdir(test_dir)

"""## Предобработка датасета"""

# Функция создания подвыборок (папок с файлами)
def create_dataset(
    img_path: str,         # Путь к файлам с изображениями классов
    new_path: str,         # Путь к папке с выборками
    class_name: str,       # Имя класса (оно же и имя папки)
    start_index: int,      # Стартовый индекс изображения, с которого начинаем подвыборку
    end_index: int         # Конечный индекс изображения, до которого создаем подвыборку

):

    src_path = os.path.join(img_path, class_name)  # Полный путь к папке с изображениями класса
    dst_path = os.path.join(new_path, class_name)  # Полный путь к папке с новым датасетом класса

    # Получение списка имен файлов с изображениями текущего класса
    class_files = os.listdir(src_path)

    # Создаем подпапку, используя путь
    os.mkdir(dst_path)

    # Перебираем элементы, отобранного списка с начального по конечный индекс
    for fname in class_files[start_index : end_index]:
        # Путь к файлу (источник)
        src = os.path.join(src_path, fname)
        # Новый путь расположения файла (назначение)
        dst = os.path.join(dst_path, fname)
        # Копируем файл из источника в новое место (назначение)
        shutil.copyfile(src, dst)

for class_label in range(CLASS_COUNT):    # Перебор по всем классам по порядку номеров (их меток)
    class_name = CLASS_LIST[class_label]  # Выборка имени класса из списка имен

    # Создаем обучающую выборку для заданного класса из диапазона (0-1500)
    create_dataset(IMAGE_PATH, train_dir, class_name, 0, 1500)
    # Создаем проверочную выборку для заданного класса из диапазона (1500-2000)
    create_dataset(IMAGE_PATH, test_dir, class_name, 1500, 2000)

datagen = ImageDataGenerator(rescale=1./255) # Задаем генератор и нормализуем данные делением на 255
batch_size = 20 # Размер батча (20 изображений)

# Функция извлечения признаков
def extract_features(directory, sample_count):
    # определяем размерность признаков, заполняем нулями
    features = np.zeros(shape=(sample_count, 4, 4, 512))
    # определяем размерность выходных меток, заполняем нулями
    labels = np.zeros(shape=(sample_count))

    # генерируем данные из папки
    generator = datagen.flow_from_directory(
        directory,                # путь к папке
        target_size=(150, 150),   # изменить картинки до размера 150 х 150
        batch_size=batch_size,    # размер пакета
        class_mode='binary'       # задача бинарной классификации
    )
    i = 0
    for inputs_batch, labels_batch in generator: # в цикле пошагово генерируем пакет с картинками и пакет из меток
        features_batch = conv_base.predict(inputs_batch, verbose=0) # делаем предсказание на сгенерируемом пакете
        features[i * batch_size : (i + 1) * batch_size] = features_batch # складываем пакеты с признаками пачками в массив с признаками

        labels[i * batch_size : (i + 1) * batch_size] = labels_batch     # складываем пакеты с метками в массив с метками
        i += 1

        if i * batch_size >= sample_count: # Прерываем генерацию, когда выходим за число желаемых примеров
            break

    return features, labels # возвращаем кортеж (признаки, метки)

# Извлекаем (признаки, метки) для обучающей выборки, 2500 образцов
train_features, train_labels = extract_features(train_dir, 2500)

# Извлекаем (признаки, метки) для проверочной выборки, 1500 образцов
test_features, test_labels = extract_features(test_dir, 1500)

train_features = np.reshape(train_features, (2500, 4 * 4 * 512))              # приводим к форме (образцы, 8192) обучающие признаки
test_features = np.reshape(test_features, (1500, 4 * 4 * 512))    # приводим к форме (образцы, 8192) проверочные признаки

"""# Реализация ГА для подбора гиперпараметров

## Диапазон подбора
"""

param_ranges = {
    "learning_rate": (2e-5, 0.1),
    "num_layers": (1, 6),
    "num_neurons": (100, 500),
    "activation": ['relu', 'tanh'],
    "batch_size": (16, 256),  # Увеличен минимальный размер батча
    "dropout_rate": (0.1, 0.4)  # Ограничен диапазон Dropout
}

def random_params():
    return (
        random.uniform(*param_ranges["learning_rate"]),
        random.randint(*param_ranges["num_layers"]),
        random.randint(*param_ranges["num_neurons"]),
        random.choice(param_ranges["activation"]),
        random.randint(*param_ranges["batch_size"]),
        random.uniform(*param_ranges["dropout_rate"])
    )

"""## Функция компиляции модели и подсчет весовых коэфициентов"""

def fitness_function(params):
    learning_rate, num_layers, num_neurons, activation, batch_size, dropout_rate = params

    model = Sequential()
    model.add(Input(shape=(4 * 4 * 512,)))
    for _ in range(num_layers - 1):
        model.add(Dense(num_neurons, activation=activation))
        model.add(Dropout(dropout_rate))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer=optimizers.RMSprop(learning_rate=learning_rate),
                  loss='binary_crossentropy', metrics=['accuracy'])

    start_time = time.time()
    model.fit(train_features,
              train_labels, epochs=5,
              batch_size=batch_size,
              verbose=0)
    end_time = time.time()

    training_time = end_time - start_time
    y_pred_probs = model.predict(test_features, verbose=0)
    y_pred = (y_pred_probs > 0.5).astype(int)  # Бинаризация предсказаний
    accuracy = accuracy_score(test_labels, y_pred)

    # Итоговый балл с использованием весовых коэффициентов
    weight_accuracy = 0.8  # Вес для точности
    weight_time = 0.2      # Вес для времени обучения
    score = (weight_accuracy * accuracy) - (weight_time * training_time)

    return score, accuracy, training_time

"""## Реализация генетического алгоритма"""

# Генетический алгоритм
def genetic_algorithm(population_size, num_generations, mutation_rate):
    population = []  # Инициализация популяции
    for _ in range(population_size):
        population.append(random_params())

    best_fitness = 0
    best_individual = None
    best_accuracy = None
    best_training_time = None


    for generation in range(num_generations):
        print(f"\nПоколение {generation + 1}/{num_generations}")

        fitness_scores = []
        for idx, individual in enumerate(population):
            score, accuracy, training_time = fitness_function(individual)
            fitness_scores.append((score, accuracy, training_time))
            print(f"Особь {idx + 1}: LR={individual[0]:.4f}, "
                  f"Слои={individual[1]}, Нейроны={individual[2]}, "
                  f"Активация={individual[3]}, Batch={individual[4]}, "
                  f"Dropout={individual[5]:.2f}, accuracy={accuracy:.4f}, "
                  f"Время={training_time:.2f} сек, Итоговый балл={score:.4f}")

        current_best_idx = np.argmax([fs[0] for fs in fitness_scores])  # Индекс лучшего score
        current_best_fitness, current_best_accuracy, current_best_training_time = fitness_scores[current_best_idx]
        current_best_individual = population[current_best_idx]

        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = current_best_individual
            best_accuracy = current_best_accuracy
            best_training_time = current_best_training_time
            print(f"\nНовый лучший результат!")
            print(f"Параметры: LR={best_individual[0]:.4f}, "
                f"Слои={best_individual[1]}, Нейроны={best_individual[2]}, "
                f"Активация={best_individual[3]}, Batch={best_individual[4]}, "
                f"Dropout={best_individual[5]:.2f}")
            print(f"accuracy: {best_accuracy:.4f}, Время: {best_training_time:.2f} сек, Итоговый балл: {best_fitness:.4f}")



        # Селекция
        selected_population = []
        for _ in range(population_size):
            tournament = random.sample(list(zip(population, fitness_scores)), 3)
            winner = max(tournament, key=lambda x: x[1])[0]
            selected_population.append(winner)

        # Создание нового поколения
        new_population = []
        for i in range(0, population_size, 2):
            parent1, parent2 = selected_population[i], selected_population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            new_population.extend([child1, child2])

        population = new_population

    return best_individual, best_fitness, best_accuracy, best_training_time

def crossover(parent1, parent2):
    child1 = (
        parent1[0],  # Learning rate от первого родителя
        parent2[1],  # Количество слоев от второго родителя
        parent1[2],  # Нейроны от первого родителя
        parent2[3],  # Активация от второго родителя
        parent1[4],  # Batch size от первого родителя
        parent2[5]   # Dropout от второго родителя
    )
    child2 = (
        parent2[0],
        parent1[1],
        parent2[2],
        parent1[3],
        parent2[4],
        parent1[5]
    )
    return child1, child2

def mutate(individual, mutation_rate):
    if random.random() < mutation_rate:
        return random_params()  # Генерация новой особи
    return individual

"""## Запуск обучения"""

# Запуск генетического алгоритма
population_size = 10
num_generations = 10
mutation_rate = 0.1

best_params, best_fitness, best_accuracy, best_training_time = genetic_algorithm(population_size, num_generations, mutation_rate)
print("\nИтоговые результаты:")
print(f"Лучшие гиперпараметры: LR={best_params[0]:.4f}, Слои={best_params[1]}, "
      f"Нейроны={best_params[2]}, Активация={best_params[3]}, Batch={best_params[4]}, Dropout={best_params[5]:.2f}")
print(f"Лучшая accuracy: {best_accuracy:.4f}, Время: {best_training_time:.2f} сек, Итоговый балл: {best_fitness:.4f}")

"""# Итоги

Выявлена модель, показывающая наибольшый итоговый балл.

Итоговый балл - разность весовых коэфициентов точности и времени обучения модели.

Гиперпараметры подобраны с помощью генетического алгоритма.

В качестве набора данных используется датасет Cats and Dogs.
"""