`timescale 1ns / 1ps

// Table 5 defines the optional interface to the device-specific transceiver or to the LVDS SelectIO technology
//transceiver implementation. The core is connected to the chosen transceiver in the HDL example design delivered
//with the core. For a complete description of the device-specific transceiver interface, see the transceiver user guide
//specific to your device. (For user guide information, see [Ref 6], [Ref 7], and [Ref 8] at the end of this document.)
module SGMIICore(

    // Connect to RXRESET signal of the transceiver.
    input mgt_rx_reset,
    // Connect to TXRESET signal of the transceiver.
    input mgt_tx_reset,
    // Also connected to TXUSRCLK and RXUSRCLK of the device-specific transceiver.
    output userclk,
    // Also connected to TXUSRCLK2 and RXUSRCLK2 of the device-specific transceiver.
    output userclk2,
    // A Digital Clock Manager (DCM) can be used to derive userclk and
    //userclk2. This is implemented in the HDL design example delivered with the core.
    output dcm_locked


);

endmodule