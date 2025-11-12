/**
 * @file receive_buffer.c
 * @brief Implementation of a buffer to store data received from the PL/PS interface.
 * @author Florian Frank
 * @copyright University of Passau - Chair of Computer Engineering
 */

#include "receive_buffer.h"
#include "malloc.h"
#include "logging.h"

#define BUFFER_SIZE 2048

BufferElement *recvBuffer;
uint32_t readIndexCtr;
uint32_t writeIndexCtr;

uint64_t overallWriteCtr;
uint64_t overallReadCtr;

/**
 * @brief Initializes the receive buffer and allocates memory.
 * @return 0 on success, -1 if memory allocation fails.
 */
int initializeBuffer() {
    log_message(LOG_INFO, _FILE_NAME_, __LINE__, "Setup receive Buffer of size %x", BUFFER_SIZE);
    recvBuffer = malloc(BUFFER_SIZE * sizeof(BufferElement));
    if(recvBuffer){
        readIndexCtr = 0;
        writeIndexCtr = 0;
        overallWriteCtr = 0;
        return 0;
    }
    return -1;
}

/**
 * @brief Frees memory allocated for the receive buffer.
 */
void deInitializeBuffer() {
    free(recvBuffer);
}

/**
 * @brief Adds an element to the reception buffer.
 * @param bufferElem Pointer to the element to add.
 * @note TODO Currently increments write index by 16; ensure it does not overwrite unread elements.
 */
void addElementToRecvBuffer(const BufferElement *bufferElem) {
    memcpy(&recvBuffer[writeIndexCtr], bufferElem, sizeof(BufferElement));
    overallWriteCtr++;
    writeIndexCtr = (writeIndexCtr + 16) % BUFFER_SIZE;
}

/**
 * @brief Pops the next available element from the receive buffer.
 * @param recvElement Pointer to the structure where the popped element will be stored.
 * @return 1 if an element was successfully popped, 0 if the buffer is empty.
 */
int popElementFromRecvBuffer(BufferElement *recvElement){
    if (overallReadCtr < overallWriteCtr) {
        memcpy(recvElement, &recvBuffer[readIndexCtr], sizeof(BufferElement));
        overallReadCtr++;
        readIndexCtr = (readIndexCtr + 16) % BUFFER_SIZE;
        return 1;
    }
    return 0;
}