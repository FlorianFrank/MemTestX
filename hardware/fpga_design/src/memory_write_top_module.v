`timescale 1ns / 1ps

//% \addtogroup memctr Memory Controller
//% @{

//% @brief This module is responsible for writing to a Rohm FRAM memory module.
//% It sets the OE, WE, CS, as well as the address and data lines accordingly. 
//% @author Florian Frank
//% @copyright University of Passau - Chair of Computer Engineering
module memory_write_top_module #(
    parameter integer FREQ_CLK1 = 100,
    parameter integer FREQ_CLK2 = 400,
    parameter integer ADDRESS_BUS_SIZE = 15,
    parameter integer DATA_BUS_SIZE = 8,
    parameter integer DATA_BUS_SIZE_OUT = 8,
    parameter integer CLOCK_CONFIG_WIDTH = 16
) (
    //% Input clock to trigger the always block executing the state machine.    
    input wire clk,
    input wire set_back,
    input wire start_write,

    //% Input value which should be written to the memory module.
    input wire [DATA_BUS_SIZE-1:0] value_write,
    input wire [ADDRESS_BUS_SIZE-1:0] address_write,

    //% Data lines to write the values to.
    output reg [DATA_BUS_SIZE_OUT-1:0] dlines,
    //% Address lines to select the specific cell.
    output reg [ADDRESS_BUS_SIZE-1:0] alines,
    //% Chip enable signal which is set accordingly.
    output reg ce,
    //% Output enable signal set by the memory controller.
    output reg oe,
    //% Write enable signal set by the memory controller.
    output reg we,


    input wire[ADDRESS_BUS_SIZE-1:0] max_address,

    //% Wire indicating whether the data was written.
    input wire write_continously,
    input wire ceDriven,
    input wire [CLOCK_CONFIG_WIDTH-1:0] tnext,
    input wire [CLOCK_CONFIG_WIDTH-1:0] tStart, // Delay before start
    input wire [CLOCK_CONFIG_WIDTH-1:0] tac,    // Access time
    input wire [CLOCK_CONFIG_WIDTH-1:0] tas,     // Address setup time
    input wire [CLOCK_CONFIG_WIDTH-1:0] tah,     // Address hold time
    input wire [CLOCK_CONFIG_WIDTH-1:0] tds,     // Data setup time
    input wire [CLOCK_CONFIG_WIDTH-1:0] tdh,     // Data hold time
    input wire [CLOCK_CONFIG_WIDTH-1:0] tpwd,    // Pulse width duration

    output reg write_active,
    output reg write_done,
    output wire[3:0] state_mem
);

    localparam [3:0] INITIALIZE         = 4'h0;
    localparam [3:0] ACTIVATE           = 4'h1;
    localparam [3:0] SET_DATA           = 4'h2;
    localparam [3:0] DISABLE_CE_OE      = 4'h3;
    localparam [3:0] NEXT_ROUND         = 4'h4;
    localparam [3:0] FINISH             = 4'h5;
    


    reg [CLOCK_CONFIG_WIDTH-1:0] counter = 0;
    reg [CLOCK_CONFIG_WIDTH-1:0] counter2 = 0;
    reg [3:0] state_reg = INITIALIZE;
    reg [7:0] round_ctr = 0;
    reg started = 0;
    reg waited = 0;    

    reg [DATA_BUS_SIZE-1:0] value_tmp;
    reg [DATA_BUS_SIZE_OUT-1:0] out_value;
    reg [ADDRESS_BUS_SIZE-1:0] address_tmp;
    reg [7:0] clk_sync_ctr = 0;
    reg [7:0] clock_buff_ctr = 0;



    //% Initial block initializes all values to default.
    initial begin
        counter <= 0;
        counter2 <= 0;
        state_reg <= 0;
        clk_sync_ctr <= 0;
        value_tmp <= 0;
        address_tmp <= 0;
        write_done <= 0;
        write_active <= 0;
        alines <= {ADDRESS_BUS_SIZE{1'b0}};
        dlines <= {DATA_BUS_SIZE_OUT{1'b0}};
        we <= 1;
        oe <= 1;
        ce <= 1;
    end


    //% Always block to execute the state machine.
    always @ (posedge clk) begin //or posedge reset) begin
        if (set_back) begin
            counter <= 0;
            state_reg <= 0;
            clk_sync_ctr <= 0;
            value_tmp <= 0;
            address_tmp <= 0;
            write_done <= 0;
            write_active <= 0;
            alines <= {ADDRESS_BUS_SIZE{1'b0}};
            dlines <= {DATA_BUS_SIZE_OUT{1'b0}};
            we <= 1;
            oe <= 1;
            ce <= 1;
            waited <= 0;
        end else begin
            case (state_reg)
                INITIALIZE: begin
                    write_done <= 0;
                    
                    // Wait til start signal from controller
                    if (start_write || started) begin
                        started <= 1;
                        value_tmp <= value_write;
                        address_tmp <= address_write;
                        ce <= 1; oe <= 1; we <= 1;
                        clock_buff_ctr <= 0;
                        out_value <= value_write[DATA_BUS_SIZE_OUT-1:0];
                        write_active <= 1;                        
                        if (counter == tStart) begin
                            started <= 0;
                            state_reg <= ACTIVATE;
                            counter <= 0;
                        end else begin 
                            counter <= counter + 1;
                        end
                    end else begin
                        write_active <= 0;
                    end
                end

                // This state activates either the CE signal if CE controlled or it activates the WE signal if WE controlled
                // Waits for the address setup time to set the corresponding addresses
                ACTIVATE: begin
                    write_active <= 1;                        
                    write_done <= 0;
                    if (ceDriven == 1'b1) begin
                        ce <= 0;
                        oe <= 1;
                        if (tas == 8'h0 || counter == tas) begin
                            we <= 0;
                            clock_buff_ctr <= clock_buff_ctr + 1;
                            alines <= address_tmp;
                            state_reg <= SET_DATA;
                            counter <= 0;
                        end
                        else begin 
                            counter <= counter + 1;
                        end
                    end else begin
                        we <= 0;
                        if (tas == 8'h0 || counter == tas) begin
                            ce <= 0;
                            counter <= 0;
                            clock_buff_ctr <= clock_buff_ctr + 1;
                            alines <= address_tmp;
                            state_reg <= SET_DATA;
                        end else begin 
                            counter <= counter + 1;
                        end
                    end
                end

                SET_DATA: begin
                    write_active <= 1;
                    write_done <= 0;
                    oe <= 1;
                    we <= 0;
                    ce <= 0;

                    if (tac == 0 || counter == (tac - 1)) begin
                        dlines <= value_write;
                        counter <= 0;
                        state_reg <= DISABLE_CE_OE;
                    end
                    else begin 
                        counter <= counter + 1;
                    end
                end

                // Finish the write/read operation by setting the OE and CE labels to high abain
                DISABLE_CE_OE: begin
                    write_active <= 1;
                    write_done <= 0;
                    oe <= 1;
                    if (tds == 0 || counter == (tds - 1)) begin
                        if (ceDriven == 1'b1) begin
                            we <= 1;
                            if (tdh == 8'h0 || counter2 == tdh) begin
                                ce <= 1;
                                counter2 <= 0;
                                counter <= 0;
                                if ((~write_continously && clock_buff_ctr < DATA_BUS_SIZE / DATA_BUS_SIZE_OUT) || (write_continously && address_tmp < max_address))
                                    state_reg <= NEXT_ROUND;
                                else 
                                    state_reg <= FINISH;
                            end else begin 
                                ce <= 0;
                                counter2 <= counter2 + 1;
                            end
                        end else begin
                            ce <= 1;
                            if (tdh == 8'h0 || counter2 == tdh) begin
                                we <= 1;
                                counter2 <= 0;
                                counter <= 0;
                                if ((~write_continously && clock_buff_ctr < DATA_BUS_SIZE / DATA_BUS_SIZE_OUT) || (write_continously && address_tmp < max_address))
                                    state_reg <= NEXT_ROUND;
                                else 
                                    state_reg <= FINISH;
                            end else begin 
                                we <= 0;
                                counter2 <= counter2 + 1;
                            end
                        end
                    end else begin 
                        counter <= counter + 1;
                    end
                end

                NEXT_ROUND: begin
                    write_active <= 1;
                    write_done <= 0;
                    ce <= 1; we <= 1; oe <= 1;
                    out_value <= value_tmp[clock_buff_ctr * DATA_BUS_SIZE_OUT+:DATA_BUS_SIZE_OUT];
                    if (tnext == 0 || counter == (tnext-2)) begin
                        counter <= 0; 
                        address_tmp <= address_tmp + 1;
                        state_reg <= ACTIVATE;
                    end else begin 
                        counter <= counter + 1;
                    end
                    
                end

                FINISH: begin
                    ce <= 1; we <= 1; oe <= 1;
                    write_active <= 0;
                    write_done <= 1;
                    if (clk_sync_ctr < FREQ_CLK2 / FREQ_CLK1) begin
                        clk_sync_ctr <= clk_sync_ctr + 1;
                    end else begin
                        clk_sync_ctr <= 0;
                        if (tnext == 0 || counter == tnext) begin
                            counter <= 0; 
                            state_reg <= INITIALIZE;
                        end else begin
                            counter <= counter + 1;
                        end
                    end
                end
            endcase
        end
    end
    
    assign state_mem =  state_reg;

endmodule
//% @}
