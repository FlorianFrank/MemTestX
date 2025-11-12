/**
* @file receive_buffer.h
 * @brief Implementation of a buffer to store data received from the PL/PS interface.
 * @author Florian Frank
 * @copyright University of Passau - Chair of Computer Engineering
 */

#ifndef _RECEIVE_BUFFER_H
#define _RECEIVE_BUFFER_H

#include <stdint.h>

struct BufferElement {
    uint32_t preamble;
    uint32_t address;
    uint32_t value;
    uint32_t checksum;
} typedef BufferElement;

int initializeBuffer();
void deInitializeBuffer();
void addElementToRecvBuffer(const BufferElement *bufferElem);
int popElementFromRecvBuffer(BufferElement *recvElement);
#endif // _RECEIVE_BUFFER_H
