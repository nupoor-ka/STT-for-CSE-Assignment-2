#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    int n, choice = -1, i, j, temp, key, k, repeat;
    int arr[100];
    srand(time(NULL));

    printf("Enter number of elements (max 100): ");
    scanf("%d", &n);

    printf("Choose input method:\n1. Enter manually\n2. Generate randomly\n");
    scanf("%d", &choice);

    if (choice == 1) {
        for (i = 0; i < n; i++) {
            printf("Enter element %d: ", i + 1);
            scanf("%d", &arr[i]);
        }
    } else {
        for (i = 0; i < n; i++) {
            arr[i] = rand() % 1000;
        }
        printf("Random array generated:\n");
        for (i = 0; i < n; i++) {
            printf("%d ", arr[i]);
        }
        printf("\n");
    }

    choice = -1;
    while (choice != 0) {
        printf("\n=== Sorting & Searching Suite ===\n");
        printf("1. Bubble Sort\n");
        printf("2. Insertion Sort\n");
        printf("3. Merge Sort\n");
        printf("4. Quick Sort\n");
        printf("5. Linear Search\n");
        printf("6. Binary Search\n");
        printf("7. Print Array\n");
        printf("8. Count Inversions\n");
        printf("9. Find kth Largest / Smallest\n");
        printf("10. Reverse Array\n");
        printf("11. Shuffle Array\n");
        printf("0. Exit\n");
        printf("Enter choice: ");
        scanf("%d", &choice);

        if (choice == 1) { // Bubble Sort
            for (i = 0; i < n - 1; i++) {
                for (j = 0; j < n - i - 1; j++) {
                    if (arr[j] > arr[j + 1]) {
                        temp = arr[j];
                        arr[j] = arr[j + 1];
                        arr[j + 1] = temp;
                    }
                }
            }
            printf("Array sorted using Bubble Sort.\n");
        }
        else if (choice == 2) { // Insertion Sort
            for (i = 1; i < n; i++) {
                temp = arr[i];
                j = i - 1;
                while (j >= 0 && arr[j] > temp) {
                    arr[j + 1] = arr[j];
                    j--;
                }
                arr[j + 1] = temp;
            }
            printf("Array sorted using Insertion Sort.\n");
        }
        else if (choice == 3) { // Merge Sort
            int width, left, right, mid, l, r;
            int temp_arr[100];
            for (width = 1; width < n; width *= 2) {
                for (i = 0; i < n; i += 2 * width) {
                    left = i;
                    mid = i + width - 1;
                    right = i + 2 * width - 1;
                    if (mid >= n) {
                        mid = n - 1;
                    }
                    if (right >= n) {
                        right = n - 1;
                    }
                    l = left;
                    r = mid + 1;
                    j = left;
                    while (l <= mid && r <= right) {
                        if (arr[l] <= arr[r]) {
                            temp_arr[j++] = arr[l++];
                        } else {
                            temp_arr[j++] = arr[r++];
                        }
                    }
                    while (l <= mid) {
                        temp_arr[j++] = arr[l++];
                    }
                    while (r <= right) {
                        temp_arr[j++] = arr[r++];
                    }
                    for (j = left; j <= right; j++) {
                        arr[j] = temp_arr[j];
                    }
                }
            }
            printf("Array sorted using Merge Sort.\n");
        }
        else if (choice == 4) { // Quick Sort (Iterative)
            int stack[100], top = -1, low, high, pivot, p;
            stack[++top] = 0;
            stack[++top] = n - 1;
            while (top >= 0) {
                high = stack[top--];
                low = stack[top--];
                pivot = arr[high];
                i = low - 1;
                for (j = low; j <= high - 1; j++) {
                    if (arr[j] < pivot) {
                        i++;
                        temp = arr[i];
                        arr[i] = arr[j];
                        arr[j] = temp;
                    }
                }
                temp = arr[i + 1];
                arr[i + 1] = arr[high];
                arr[high] = temp;
                p = i + 1;
                if (p - 1 > low) {
                    stack[++top] = low;
                    stack[++top] = p - 1;
                }
                if (p + 1 < high) {
                    stack[++top] = p + 1;
                    stack[++top] = high;
                }
            }
            printf("Array sorted using Quick Sort.\n");
        }
        else if (choice == 5) { // Linear Search
            printf("Enter key to search: ");
            scanf("%d", &key);
            int found = 0;
            for (i = 0; i < n; i++) {
                if (arr[i] == key) {
                    found = 1;
                    break;
                }
            }
            if (found) {
                printf("Key %d found at index %d.\n", key, i);
            } else {
                printf("Key %d not found.\n", key);
            }
        }
        else if (choice == 6) { // Binary Search
            printf("Enter key to search: ");
            scanf("%d", &key);
            int left = 0, right = n - 1, found = 0, mid;
            while (left <= right) {
                mid = (left + right) / 2;
                if (arr[mid] == key) {
                    found = 1;
                    break;
                } else if (arr[mid] < key) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
            if (found) {
                printf("Key %d found at index %d.\n", key, mid);
            } else {
                printf("Key %d not found.\n", key);
            }
        }
        else if (choice == 7) { // Print Array
            printf("Array: ");
            for (i = 0; i < n; i++) {
                printf("%d ", arr[i]);
            }
            printf("\n");
        }
        else if (choice == 8) { // Count Inversions
            int inv = 0;
            for (i = 0; i < n; i++) {
                for (j = i + 1; j < n; j++) {
                    if (arr[i] > arr[j]) {
                        inv++;
                    }
                }
            }
            printf("Number of inversions: %d\n", inv);
        }
        else if (choice == 9) { // kth Largest / Smallest
            int temp_arr[100];
            for (i = 0; i < n; i++) {
                temp_arr[i] = arr[i];
            }
            for (i = 0; i < n - 1; i++) {
                for (j = 0; j < n - i - 1; j++) {
                    if (temp_arr[j] > temp_arr[j + 1]) {
                        temp = temp_arr[j];
                        temp_arr[j] = temp_arr[j + 1];
                        temp_arr[j + 1] = temp;
                    }
                }
            }
            printf("Enter k (1-%d): ", n);
            scanf("%d", &k);
            if (k >= 1 && k <= n) {
                printf("k-th smallest: %d, k-th largest: %d\n", temp_arr[k - 1], temp_arr[n - k]);
            } else {
                printf("Invalid k.\n");
            }
        }
        else if (choice == 10) { // Reverse Array
            for (i = 0; i < n / 2; i++) {
                temp = arr[i];
                arr[i] = arr[n - i - 1];
                arr[n - i - 1] = temp;
            }
            printf("Array reversed.\n");
        }
        else if (choice == 11) { // Shuffle Array
            for (i = n - 1; i > 0; i--) {
                j = rand() % (i + 1);
                temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
            printf("Array shuffled.\n");
        }
        else if (choice != 0) {
            printf("Invalid option. Try again.\n");
        }
    }

    printf("Final Array:\n");
    for (i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\nExiting program.\n");

    printf("Final Array:\n");
    for (i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    // Extra statistics
    int sum = 0, min = arr[0], max = arr[0];
    for (i = 0; i < n; i++) {
        sum += arr[i];
        if (arr[i] < min) {
            min = arr[i];
        }
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    printf("Array Statistics:\n");
    printf("Sum: %d\n", sum);
    printf("Average: %.2f\n", sum / (float)n);
    printf("Min: %d, Max: %d\n", min, max);

    // Ask user if they want to repeat the program
    printf("Do you want to run another array? Enter 1 for yes, 0 for no: ");
    scanf("%d", &repeat);
    if (repeat == 1) {
        printf("Restart the program to input a new array.\n");
    }

    printf("Exiting program.\n");
    return 0;
}