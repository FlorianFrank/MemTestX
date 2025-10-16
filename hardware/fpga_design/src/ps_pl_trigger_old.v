module ps_pl_trigger(
    input wire clk,
    input wire axi_master_done,
    output reg trigger_axi_master_start,
    output wire[31:0] output_address,
    output wire[15:0] output_data
);

    parameter [3:0] INIT = 4'h00;
    parameter [3:0] TRIGGER = 4'h01;
    parameter [3:0] WAIT_FOR_START = 4'h02;
    parameter [3:0] WAIT_FINISH = 4'h03;
    parameter [3:0] SLEEP = 4'h04;

    reg [3:0] state = INIT;
    integer ctr = 0;
    reg[31:0] output_address_tmp = 0;
    reg[15:0] output_data_tmp = 16'hffff;
    
    
    assign output_address = output_address_tmp;
    assign output_data = output_data_tmp;


    always @(posedge clk) begin
        case (state) 
            INIT: begin 
                trigger_axi_master_start <= 1'b0;
                if (ctr < 1000000)
                    ctr <= ctr + 1;
                else begin
                    ctr <= 0;
                    state <= TRIGGER;
                end
            end
            TRIGGER: begin
               trigger_axi_master_start <= 1'b1;
               state <= WAIT_FOR_START;
            end
            
            WAIT_FOR_START: begin
                if(axi_master_done == 1'b0) begin
                    trigger_axi_master_start <= 1'b0;
                    state <= WAIT_FINISH;
                    end
                else 
                  trigger_axi_master_start <= 1'b1;
            end
            
            WAIT_FINISH: begin
                if (axi_master_done == 1'b1 && ctr == 1000000) begin
                    state <= SLEEP;
                    ctr <= 0;
                    trigger_axi_master_start <= 1'b0;
                    output_address_tmp <= output_address_tmp + 32'h1;
                    output_data_tmp <= output_data_tmp - 16'h1;
                 end
                 else begin
                    state <= WAIT_FINISH;
                    ctr <= ctr + 1;
                 end
            end
            SLEEP: begin
              if (ctr < 1000)
                    ctr <= ctr + 1;
                else begin
                    ctr <= 0;
                    state <= TRIGGER;
                end
            end
        endcase
    end
endmodule
