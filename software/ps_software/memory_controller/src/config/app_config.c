/**
 * @file    app_config.c
 * @brief   Fallback IP settings. In case DHCP is disabled or failes.
 *
 * @author  Florian Frank
 * @affiliation University of Passau
 * @date    2025
 */

#include "app_config.h"

int SRC_IP_V4[4] =     {192, 168,   1, 10};
int NET_MASK_V4[4] =   {255, 255, 255,  0};
int DEFAULT_GW_V4[4] = {192, 168,   1,  1};
