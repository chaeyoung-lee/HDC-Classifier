#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define IMAGE_SIZE 28
#define N_CLASS 10
#define N_DIM 10000
#define LOAD 1
#define STORE 0

typedef struct Image {
    int pixels[IMAGE_SIZE][IMAGE_SIZE];
    int label;
} Image;

uint8_t** allocate_table(int x, int y);
void free_table(uint8_t** table, int rows);
uint8_t** load_table(char* name, int row, int column);
void store_table(uint8_t** table, char* name, int row, int column);
int predict(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table, uint8_t** item_memory);
uint8_t* encode(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table);
void bind(uint8_t* x1, uint8_t* x2, uint8_t* result);
void bundle(uint8_t** xs, uint8_t* result, int length);
void permute(uint8_t* x, int length);
double distance(uint8_t* x1, uint8_t* x2);

// Main function to test the initialize function
int main() {
    // Table for HDC
    uint8_t** position_table;
    uint8_t** item_memory;

    // Load array
    if (LOAD) {
        position_table = load_table("model/codebook_56_10000.data", IMAGE_SIZE * 2, N_DIM);
        item_memory = load_table("model/model_10_10000.data", IMAGE_SIZE * 2, N_DIM);
    } else {
        position_table = allocate_table(IMAGE_SIZE * 2, N_DIM);
        item_memory = allocate_table(N_CLASS, N_DIM);
    }

    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            printf("%d ", item_memory[i][j]);
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
    printf("label: %d\n", predicted_label);

    // Store array
    if (STORE) {
        store_table(position_table, "position_table.data", IMAGE_SIZE * 2, N_DIM);
        store_table(item_memory, "item_memory.data", N_CLASS, N_DIM);
    }
    
    // Freeing dynamically allocated memory
    free_table(position_table, IMAGE_SIZE * 2);
    free_table(item_memory, N_CLASS);
    
    return 0;
}

// Function to initialize the position_table
uint8_t** allocate_table(int x, int y) {
    // Dynamically allocating a 2D array
    uint8_t** table = (uint8_t**)malloc((x) * sizeof(uint8_t*));
    for(int i = 0; i < x; i++) {
        table[i] = (uint8_t*)malloc(y * sizeof(uint8_t));
    }
    
    srand(time(NULL)); // Seed for random number generation
    
    // Filling the table with random 0s and 1s
    for(int i = 0; i < x; i++) {
        for(int j = 0; j < y; j++) {
            table[i][j] = rand() % 2;
        }
    }
    
    return table;
}

// Function to free a dynamically allocated 2D array
void free_table(uint8_t** table, int rows) {
    for (int i = 0; i < rows; i++) {
        free(table[i]); // Free each row
    }
    free(table); // Free the array of pointers
}

// Function to load a table from a binary file
uint8_t** load_table(char* name, int row, int column) {
    // Open the binary file for reading
    FILE* file = fopen(name, "rb");
    if (!file) {
        fprintf(stderr, "Failed to open the file for reading.\n");
        return 0;
    }

    // Read the dimensions (number of rows and columns) from the file
    fread(&row, sizeof(int), 1, file);
    fread(&column, sizeof(int), 1, file);

    // Allocate memory for the 2D array
    uint8_t** table = (uint8_t**)malloc(row * sizeof(uint8_t*));
    for (int i = 0; i < row; i++) {
        table[i] = (uint8_t*)malloc(column * sizeof(uint8_t));
    }

    // Read the 2D array data from the file
    for (int i = 0; i < row; i++) {
        fread(table[i], sizeof(uint8_t), column, file);
    }

    // Close the file
    fclose(file);

    return table;
}

// Function to save a table into a binary file
void store_table(uint8_t** table, char* name, int row, int column) {
    // Open a binary file for writing
    FILE* file = fopen(name, "wb");
    if (!file) {
        fprintf(stderr, "Failed to open the file for writing.\n");
        return ;
    }

    // Write the dimensions (number of rows and columns) to the file
    fwrite(&row, sizeof(int), 1, file);
    fwrite(&column, sizeof(int), 1, file);

    // Write the 2D array data to the file
    for (int i = 0; i < row; i++) {
        fwrite(table[i], sizeof(uint8_t), column, file);
    }

    // Close the file
    fclose(file);
}

// Function to predict the class label of given image
int predict(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table, uint8_t** item_memory) {
    uint8_t* encoded_image = encode(image, position_table); // should be free'ed!

    // Predict distance between encoded image and all items in the item_memory
    int label = 0;
    double score = distance(encoded_image, item_memory[0]);
    for (int i = 1; i < N_CLASS; i ++) {
        double dist = distance(encoded_image, item_memory[i]);
        if (dist < score) {
            // Update lowest score and label
            score = dist;
            label = i;
        }
    }

    free(encoded_image);
    return label;
}

// Function to encode the image by converting it to a hyperdimensional vector
uint8_t* encode(int image[IMAGE_SIZE][IMAGE_SIZE], uint8_t** position_table) {
    uint8_t** hv_all = (uint8_t**)malloc(sizeof(uint8_t*) * (IMAGE_SIZE * IMAGE_SIZE)); // [IMAGE_SIZE * IMAGE_SIZE][N_DIM]
    for (int i = 0; i < IMAGE_SIZE * IMAGE_SIZE; i++) {
        hv_all[i] = (uint8_t*)malloc(sizeof(uint8_t) * N_DIM);
    }
    
    // Encode pixel values
    for (int i = 0; i < IMAGE_SIZE; i++) {
        for (int j = 0; j < IMAGE_SIZE; j++) {
            uint8_t hv[N_DIM];
            int v = image[i][j];
            bind(position_table[i], position_table[IMAGE_SIZE + j], hv);

            // Permute if white, leave if black
            if (v > 0) {
                permute(hv, N_DIM);
            }

            // Copy results
            for (int k = 0; k < N_DIM; k++) {
                hv_all[i * IMAGE_SIZE + j][k] = hv[k];
            }
        }
    }

    // Gather all pixel encoding to create one image encoding
    uint8_t* result = (uint8_t*)malloc(sizeof(uint8_t) * N_DIM);
    bundle(hv_all, result, IMAGE_SIZE * IMAGE_SIZE);

    // Free dynamically allocated memory
    for (int i = 0; i < IMAGE_SIZE * IMAGE_SIZE; i++) {
        free(hv_all[i]);
    }
    free(hv_all);

    return result;
}

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

// Function to shift (roll) an array to the right by one position
void permute(uint8_t* x, int length) {
    int temp = x[length - 1];  // Store the last element
    for (int i = length - 1; i > 0; i--) {
        x[i] = x[i - 1];  // Shift elements to the right
    }
    x[0] = temp;  // Set the first element to the stored value
}

// Function to calculate distance between two arrays
double distance(uint8_t* x1, uint8_t* x2) {
    int sum = 0;
    for (int i = 0; i < N_DIM; i++) {
        sum += (x1[i] ^ x2[i]);
    }
    return (double)sum / N_DIM;
}

