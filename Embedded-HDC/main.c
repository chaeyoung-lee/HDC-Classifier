#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define IMAGE_SIZE 28
#define N_CLASS 10
#define N_DIM 1000

typedef struct Image {
    int pixels[IMAGE_SIZE][IMAGE_SIZE];
    int label;
} Image;

uint8_t** allocate_table(int x, int y);
void free_table(uint8_t** table, int rows);
int predict(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table, uint8_t** item_memory);
uint8_t* encode(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table);
void bind(uint8_t* x1, uint8_t* x2, uint8_t* result);
void bundle(uint8_t** xs, uint8_t* result, int length);
double distance(uint8_t* x1, uint8_t* x2);

// Main function to test the initialize function
int main() {
    uint8_t** position_table = allocate_table(IMAGE_SIZE * 2, N_DIM);
    uint8_t** item_memory = allocate_table(N_CLASS, N_DIM);
    
    // Printing position_table to verify the values (Optional)
    for(int i = 0; i < IMAGE_SIZE * 2; i++) {
        for(int j = 0; j < N_DIM; j++) {
            printf("%d ", position_table[i][j]);
        }
        printf("\n");
    }

    // Capture image, here create a sample image
    Image image;
    for(int i = 0; i < IMAGE_SIZE; i++) {
        for(int j = 0; j < IMAGE_SIZE; j++) {
            image.pixels[i][j] = 0;
        }
    }
    image.label = 0;

    // Predict image using position table and item memory
    int predicted_label = predict(image.pixels, position_table, item_memory);
    
    // Freeing dynamically allocated memory
    free_table(position_table, IMAGE_SIZE * 2);
    free_table(item_memory, N_CLASS);
    
    return 0;
}

// Function to initialize the position_table
uint8_t** allocate_table(int x, int y) {
    // Dynamically allocating a 2D array
    uint8_t** position_table = (uint8_t**)malloc((x) * sizeof(uint8_t*));
    for(int i = 0; i < x; i++) {
        position_table[i] = (uint8_t*)malloc(y * sizeof(uint8_t));
    }
    
    srand(time(NULL)); // Seed for random number generation
    
    // Filling the position_table with random 0s and 1s
    for(int i = 0; i < x; i++) {
        for(int j = 0; j < y; j++) {
            position_table[i][j] = rand() % 2;
        }
    }
    
    return position_table;
}

// Function to free a dynamically allocated 2D array
void free_table(uint8_t** table, int rows) {
    for (int i = 0; i < rows; i++) {
        free(table[i]); // Free each row
    }
    free(table); // Free the array of pointers
}

// Function to predict the class label of given image
int predict(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table, uint8_t** item_memory) {
    uint8_t* encoded_image = encode(image, position_table);
}

// Function to encode the image by converting it to a hyperdimensional vector
// uint8_t* encode(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table) {
//     uint8_t hv[IMAGE_SIZE * IMAGE_SIZE][N_DIM];
//     uint8_t hv_image[IMAGE_SIZE * IMAGE_SIZE][N_DIM];
    
//     for (int i = 0; i < IMAGE_SIZE; i++) {
//         for (int j = 0; j < IMAGE_SIZE; j++) {
//             uint8_t v = image[i * IMAGE_SIZE + j];
//             bind(&position_table[i * N_DIM], &position_table[(IMAGE_SIZE + j) * N_DIM], hv[i * IMAGE_SIZE + j]);
//             if (v > 0) {
//                 // White pixel
//                 // Value encoding
//                 uint8_t temp[N_DIM];
//                 memcpy(temp, hv[i * IMAGE_SIZE + j], N_DIM);
//                 memcpy(hv[i * IMAGE_SIZE + j], &temp[1], N_DIM - 1);
//                 hv[i * IMAGE_SIZE + j][N_DIM - 1] = 0;
//             }
//         }
//     }
//     bundle(hv, IMAGE_SIZE * IMAGE_SIZE, result, N_DIM);
// }

// Function to perform bitwise XOR operation on two arrays
void bind(uint8_t* x1, uint8_t* x2, uint8_t* result) {
    for (int i = 0; i < N_DIM; i++) {
        result[i] = x1[i] ^ x2[i];
    }
}

// Function to bundle an array of arrays (2D array)
void bundle(uint8_t** xs, uint8_t* result, int length) {
    for (int i = 0; i < N_DIM; i++) {
        int sum = 0;
        for (int j = 0; j < length; j++) {
            sum += xs[j][i];
        }
        result[i] = (sum >= length / 2) ? 1 : 0;
    }
}

// Function to calculate distance between two arrays
double distance(uint8_t* x1, uint8_t* x2) {
    int sum = 0;
    for (int i = 0; i < N_DIM; i++) {
        sum += (x1[i] ^ x2[i]);
    }
    return (double)sum / N_DIM;
}

