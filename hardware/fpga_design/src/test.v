//CODE FOR IP

        // Outputs for data AXI


        output [C_S_AXI_DATA_WIDTH-1:0] slv_reg0,
        output [C_S_AXI_DATA_WIDTH-1:0] slv_reg1


        // Outputs for hypervisor AXI
        output [C_S_AXI_DATA_WIDTH-1:0] slv_reg0,
        output [C_S_AXI_DATA_WIDTH-1:0] slv_reg1,
        output [C_S_AXI_DATA_WIDTH-1:0] slv_reg2,
        output [C_S_AXI_DATA_WIDTH-1:0] slv_reg3,
        output [C_S_AXI_DATA_WIDTH-1:0] slv_reg4



        // AddUser Ports

        output wire LED_Test1,
        output wire LED_Test2,
        output wire LED_Test3,
        output wire LED_Test4,

        // hypervisor_Slave



        .slv_reg0(Guest_ID_32),
        .slv_reg1(ID_addr1_i),
        .slv_reg2(ID_addr2_i),
        .slv_reg3(ID_addr3_i),
        .slv_reg4(ID_addr4_i)



        // data_Slave


        .slv_reg0(Data1),
        .slv_reg1(Data2)

        // Add user logic here

        wire clk1;
        wire rst1;
        wire [1:0] Guest_ID_in;
        wire [C_Hypervisor_Slave_DATA_WIDTH-1:0] ID_addr1_i;
        wire [C_Hypervisor_Slave_DATA_WIDTH-1:0] ID_addr2_i;
        wire [C_Hypervisor_Slave_DATA_WIDTH-1:0] ID_addr3_i;
        wire [C_Hypervisor_Slave_DATA_WIDTH-1:0] ID_addr4_i;

        wire [C_Hypervisor_Slave_DATA_WIDTH-1:0] Guest_ID_32;

        wire [C_Data_Slave_DATA_WIDTH-1:0] Data1;
        wire [C_Data_Slave_DATA_WIDTH-1:0] Data2;

        wire [63:0] Data;

        assign Guest_ID_in = Guest_ID_32 [1:0];

        assign Data = {Data2, Data1};

        assign clk1 = data_slave_aclk;
        assign rst1 = data_slave_aresetn;

        Prototipo_IPC Prototipo_IPC(

                        .clk(clk1),
                        .rst(rst1),
                        .Guest_ID_i(Guest_ID_in),
                        .ID_addr1_i(ID_addr1_i),
                        .ID_addr2_i(ID_addr2_i),
                        .ID_addr3_i(ID_addr3_i),
                        .ID_addr4_i(ID_addr4_i),
                        .Signal_Guest_o(Signal_Guest_o),
                        .Data_i(Data),
                        .LED_test1(LED_Test1),
                        .LED_test2(LED_Test2),
                        .LED_test3(LED_Test3),
                        .LED_test4(LED_Test4)
                );


        // User logic ends


        endmodule

        module Signal_Manager(
                input clk,
                input rst,
                input [1:0] Guest_ID_i,       // Active Guest ID
                input [1:0] Dest_Guest_ID_i,  // Destination Guest ID
                input Signal_Send_Data_i,     // When Active Guest ID send data to Dest Guest ID
                output reg Signal_Guest_o     // To signal Active Guest to read new message
        );

            reg [3:0] Guest_Signal_r4;

                always @ (posedge clk) begin
                        if (rst) begin
                                Guest_Signal_r4 <= 4'b0000;
                        end
                        if(Signal_Guest_o) begin
                                Guest_Signal_r4[Guest_ID_i] <= 0;
                        end
                        if(Signal_Send_Data_i) begin
                                Guest_Signal_r4[Dest_Guest_ID_i] <= 1'b1;
                        end
                end

            always @(Guest_ID_i) begin
                    Signal_Guest_o = Guest_Signal_r4[Guest_ID_i];
            end

        endmodule


        module Prototipo_IPC(
            input clk,
                input rst,
            input [1:0]  Guest_ID_i,
            input [31:0] ID_addr1_i,
            input [31:0] ID_addr2_i,
            input [31:0] ID_addr3_i,
            input [31:0] ID_addr4_i,

            output Signal_Guest_o,

            input wire  [2047:0] Data_i,

            output reg LED_test1,
            output reg LED_test2,
            output LED_test3,
            output LED_test4
            );

            reg [1:0] Guest_ID_r2;
            reg [31:0] ID_addr1_r32;
            reg [31:0] ID_addr2_r32;
            reg [31:0] ID_addr3_r32;
            reg [31:0] ID_addr4_r32;
            reg [2047:0] Data;

            always @ (ID_addr1_i) begin
                    ID_addr1_r32 <= ID_addr1_i [31:0];
            end

            always @ (ID_addr2_i) begin
                ID_addr2_r32 <= ID_addr2_i [31:0];
            end

            always @ (ID_addr3_i) begin
                ID_addr3_r32 <= ID_addr3_i [31:0];
            end

            always @ (ID_addr4_i) begin
                ID_addr4_r32 <= ID_addr4_i [31:0];
            end

            always @ (Guest_ID_i)
                    Guest_ID_r2 <= Guest_ID_i;

            always @ (Data_i)
                    Data <= Data_i;

            wire [31:0] Dest_Guest_ID_addr_w32;
            wire [1:0]  Dest_Guest_ID_w2;

            assign Dest_Guest_ID_addr_w32 = (Guest_ID_r2 == 0) ? ID_addr1_r32 :
                                                                             (Guest_ID_r2 == 1) ? ID_addr2_r32 :
                                                                         (Guest_ID_r2 == 2) ? ID_addr3_r32 :
                                                                             (Guest_ID_r2 == 3) ? ID_addr4_r32 : 0;

            assign Dest_Guest_Addr_o = Dest_Guest_ID_addr_w32[29:0];
                assign Dest_Guest_ID_w2  = Dest_Guest_ID_addr_w32[31:30];

                wire Dest_Guest_Signal;

                assign Dest_Guest_Signal = (Data != 0) ? 1 : 0;

                Signal_Manager Signal_Manager(
                        .clk(clk),
                        .rst(rst),
                        .Guest_ID_i(Guest_ID_r2),
                        .Dest_Guest_ID_i(Dest_Guest_ID_w2),
                        .Signal_Send_Data_i(Dest_Guest_Signal),
                        .Signal_Guest_o(Signal_Guest_o)
                );




                // Led 3 e 4 will show the Data sent by the active guest
                assign LED_test3 = Data[0];
                assign LED_test4 = Data[1];

                always @(Guest_ID_i)
                begin
                    case (Guest_ID_i)
                    // Led 1 e 2 will show the address selected where the message stored
                    0: begin
                        LED_test1 = ID_addr1_r32[0];
                            LED_test2 = ID_addr1_r32[1];
                    end
                    1:begin
                        LED_test1 = ID_addr2_r32[0];
                            LED_test2 = ID_addr2_r32[1];
                    end
                    2:begin
                        LED_test1 = ID_addr3_r32[0];
                            LED_test2 = ID_addr3_r32[1];
                    end
                    3:begin
                        LED_test1 = ID_addr4_r32[0];
                            LED_test2 = ID_addr4_r32[1];
                    end
                endcase
                end




//CODE FOR SDK


#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "xil_io.h"




int main() {


        int i;


    init_platform();


    Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR + 4, 0x0); // Address Guest 1
    Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR + 8, 0x1); // Address Guest 2
    Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR + 12, 0x2); // Address Guest 3
    Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR + 16, 0x3); // Address Guest 4


    while(1){


            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR, 0x0); // Active Guest 1
            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_DATA_SLAVE_BASEADDR, 0x3);


            for (i=0; i<100000000; i++);


            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR, 0x1); // Active Guest 2
            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_DATA_SLAVE_BASEADDR, 0x2);


            for (i=0; i<100000000; i++);


            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR, 0x2); // Active Guest 3
            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_DATA_SLAVE_BASEADDR, 0x1);


            for (i=0; i<100000000; i++);


            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_HYPERVISOR_SLAVE_BASEADDR, 0x3); // Active Guest 4
            Xil_Out32(XPAR_IPC_2LITE_SLAVES_0_DATA_SLAVE_BASEADDR, 0x0);


            for (i=0; i<100000000; i++);
    }


    cleanup_platform();
    return 0;
}