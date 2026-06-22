/**
 * 排序算法集合 - 算法
 * 包含多种经典排序算法的实现
 */
package deep_learning.algorithms;

import java.util.Arrays;

public class SortingAlgorithms {

    /**
     * 冒泡排序
     * 时间复杂度: O(n²), 空间复杂度: O(1)
     */
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            boolean swapped = false;
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            if (!swapped) break;  // 优化: 如果没有交换，已经有序
        }
    }

    /**
     * 选择排序
     * 时间复杂度: O(n²), 空间复杂度: O(1)
     */
    public static void selectionSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j;
                }
            }
            int temp = arr[minIdx];
            arr[minIdx] = arr[i];
            arr[i] = temp;
        }
    }

    /**
     * 插入排序
     * 时间复杂度: O(n²), 空间复杂度: O(1)
     */
    public static void insertionSort(int[] arr) {
        int n = arr.length;
        for (int i = 1; i < n; i++) {
            int key = arr[i];
            int j = i - 1;
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }

    /**
     * 快速排序
     * 时间复杂度: O(n log n), 空间复杂度: O(log n)
     */
    public static void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pivotIndex = partition(arr, low, high);
            quickSort(arr, low, pivotIndex - 1);
            quickSort(arr, pivotIndex + 1, high);
        }
    }

    private static int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;

        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }

        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;

        return i + 1;
    }

    /**
     * 归并排序
     * 时间复杂度: O(n log n), 空间复杂度: O(n)
     */
    public static void mergeSort(int[] arr, int left, int right) {
        if (left < right) {
            int mid = left + (right - left) / 2;
            mergeSort(arr, left, mid);
            mergeSort(arr, mid + 1, right);
            merge(arr, left, mid, right);
        }
    }

    private static void merge(int[] arr, int left, int mid, int right) {
        int n1 = mid - left + 1;
        int n2 = right - mid;

        int[] leftArr = new int[n1];
        int[] rightArr = new int[n2];

        System.arraycopy(arr, left, leftArr, 0, n1);
        System.arraycopy(arr, mid + 1, rightArr, 0, n2);

        int i = 0, j = 0, k = left;
        while (i < n1 && j < n2) {
            if (leftArr[i] <= rightArr[j]) {
                arr[k] = leftArr[i];
                i++;
            } else {
                arr[k] = rightArr[j];
                j++;
            }
            k++;
        }

        while (i < n1) {
            arr[k] = leftArr[i];
            i++;
            k++;
        }

        while (j < n2) {
            arr[k] = rightArr[j];
            j++;
            k++;
        }
    }

    /**
     * 堆排序
     * 时间复杂度: O(n log n), 空间复杂度: O(1)
     */
    public static void heapSort(int[] arr) {
        int n = arr.length;

        // 构建最大堆
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(arr, n, i);
        }

        // 逐个提取元素
        for (int i = n - 1; i > 0; i--) {
            int temp = arr[0];
            arr[0] = arr[i];
            arr[i] = temp;
            heapify(arr, i, 0);
        }
    }

    private static void heapify(int[] arr, int n, int i) {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;

        if (left < n && arr[left] > arr[largest]) {
            largest = left;
        }
        if (right < n && arr[right] > arr[largest]) {
            largest = right;
        }
        if (largest != i) {
            int temp = arr[i];
            arr[i] = arr[largest];
            arr[largest] = temp;
            heapify(arr, n, largest);
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 排序算法演示 ===\n");

        int[] original = {64, 34, 25, 12, 22, 11, 90, 1, 55, 42};
        System.out.println("原始数组: " + Arrays.toString(original));

        // 测试各种排序算法
        int[] arr;

        arr = original.clone();
        bubbleSort(arr);
        System.out.println("冒泡排序: " + Arrays.toString(arr));

        arr = original.clone();
        selectionSort(arr);
        System.out.println("选择排序: " + Arrays.toString(arr));

        arr = original.clone();
        insertionSort(arr);
        System.out.println("插入排序: " + Arrays.toString(arr));

        arr = original.clone();
        quickSort(arr, 0, arr.length - 1);
        System.out.println("快速排序: " + Arrays.toString(arr));

        arr = original.clone();
        mergeSort(arr, 0, arr.length - 1);
        System.out.println("归并排序: " + Arrays.toString(arr));

        arr = original.clone();
        heapSort(arr);
        System.out.println("堆排序:   " + Arrays.toString(arr));

        // 性能比较
        System.out.println("\n=== 性能比较 (10000个随机数) ===\n");

        int size = 10000;
        int[] testData = new int[size];
        java.util.Random rand = new java.util.Random(42);
        for (int i = 0; i < size; i++) {
            testData[i] = rand.nextInt(size);
        }

        long start, end;

        arr = testData.clone();
        start = System.nanoTime();
        insertionSort(arr);
        end = System.nanoTime();
        System.out.printf("插入排序: %.2f ms%n", (end - start) / 1e6);

        arr = testData.clone();
        start = System.nanoTime();
        quickSort(arr, 0, arr.length - 1);
        end = System.nanoTime();
        System.out.printf("快速排序: %.2f ms%n", (end - start) / 1e6);

        arr = testData.clone();
        start = System.nanoTime();
        mergeSort(arr, 0, arr.length - 1);
        end = System.nanoTime();
        System.out.printf("归并排序: %.2f ms%n", (end - start) / 1e6);

        arr = testData.clone();
        start = System.nanoTime();
        heapSort(arr);
        end = System.nanoTime();
        System.out.printf("堆排序:   %.2f ms%n", (end - start) / 1e6);
    }
}
