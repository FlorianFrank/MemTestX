`timescale 1ns / 1ps

module mdio
#(parameter CLOCK_DIVIDER=50)
(
    input wire clk_125MHz,
    input wire start,
    output wire active,
    input wire reset,

    input wire read_write,
    input wire [4:0] phy_address,
    input wire [4:0] register_address,
    input wire [15:0] data,
    
    inout wire mdio,
    output wire mdc,

    output wire[3:0] state_out
);

    parameter IDLE_STATE                        = 4'h0;
    parameter START_STATE                       = 4'h1;
    parameter WRITE_OPCODE_STATE                = 4'h2;
    parameter WRITE_PHY_ADDRESS_STATE           = 4'h3;
    parameter WRITE_PHY_REGISTER_ADDRESS_STATE  = 4'h4;
    parameter WRITE_TA_STATE                    = 4'h5;
    parameter WRITE_REGISTER_DATA_STATE         = 4'h6;

    // Length definitions
    parameter [5:0] START_FLAG_LEN              = 6'h2,
                    OPCODE_LEN                  = 6'h2,
                    PHY_ADDRESS_LEN             = 6'h5,
                    REGISTER_ADDRESS_LEN        = 6'h5,
                    TA_LEN                      = 6'h2,
                    DATA_LEN                    = 6'h0f;



    // Constant definitions
    parameter READ_FLAG      = 1'b0;
    parameter WRITE_FLAG     = 1'b1;
    reg [1:0] START_SEQUENCE = 2'b10;
    reg [1:0] OPCODE_WRITE   = 2'b10;
    reg [1:0] OPCODE_READ    = 2'b01;
    reg [1:0] TA_WRITE       = 2'b01;
    reg [1:0] TA_READ        = 2'b0z;

    reg mdio_reg = 1'bz;
    reg management_clk      = 0;
    reg [7:0] clk_counter     = 0;
    reg [3:0] state           = 0;
    reg [5:0] serial_data_ctr = 0;
    reg active_tmp = 0;


    // Always block to generate the management clock
    always @(posedge clk_125MHz or posedge reset) begin
        if (reset) begin
            if (clk_counter == CLOCK_DIVIDER) begin
                management_clk <= ~management_clk;
                clk_counter <= 0;
            end
            else begin
                clk_counter <= clk_counter + 1;
            end
        end
    end

    task set_value_change_state(input value, input[3:0] next_state, input[5:0] max_len);
    begin
        mdio_reg <= value;
        if (serial_data_ctr == max_len-1) begin
            serial_data_ctr <= 0;
            state <= next_state;
        end else
            serial_data_ctr <= serial_data_ctr + 1;
    end
    endtask

    always @(posedge management_clk) begin
        case (state)
            IDLE_STATE: begin
                mdio_reg <= 1'bz;
                serial_data_ctr = 0;
                if (start) begin
                    state <= START_STATE;
                    active_tmp <= 1'b1;
                end
                else
                    active_tmp <= 1'b0;
            end
            START_STATE: begin
                set_value_change_state(START_SEQUENCE[serial_data_ctr], WRITE_OPCODE_STATE, START_FLAG_LEN);
            end

            WRITE_OPCODE_STATE: begin
                set_value_change_state((read_write == READ_FLAG) ?
                                        OPCODE_READ[serial_data_ctr] : OPCODE_WRITE[serial_data_ctr],
                                        WRITE_PHY_ADDRESS_STATE, OPCODE_LEN);
            end

            WRITE_PHY_ADDRESS_STATE: begin
                set_value_change_state(phy_address[serial_data_ctr], WRITE_PHY_REGISTER_ADDRESS_STATE, PHY_ADDRESS_LEN);
            end

            WRITE_PHY_REGISTER_ADDRESS_STATE: begin
                set_value_change_state(register_address[serial_data_ctr], WRITE_TA_STATE, REGISTER_ADDRESS_LEN);
            end

            WRITE_TA_STATE: begin
                set_value_change_state((read_write == READ_FLAG) ?
                                        TA_READ[serial_data_ctr] : TA_WRITE[serial_data_ctr],
                                        WRITE_REGISTER_DATA_STATE, TA_LEN);
            end

            WRITE_REGISTER_DATA_STATE: begin
                set_value_change_state(data[serial_data_ctr], IDLE_STATE, DATA_LEN);
            end
        endcase
    end

    assign mdio = mdio_reg;
    assign mdc = management_clk;
    assign state_out = state;
    assign active = active_tmp;

endmodule
