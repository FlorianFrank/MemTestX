
`timescale 1 ns / 1 ps


`define DEBUG 1
`define TIMING_BUS_WIDTH    16

	module ps_pl_interface_v1_0 #
	(
		// Users to add parameters here

		// User parameters ends
		// Do not modify the parameters beyond this line


		// Parameters of Axi Slave Bus Interface AXI_Light_Slave
		parameter integer C_AXI_Light_Slave_DATA_WIDTH	= 32,
		parameter integer C_AXI_Light_Slave_ADDR_WIDTH	= 20,

		// Parameters of Axi Master Bus Interface AXI_Light_Master
		parameter  C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR	= 32'h40000000,
		parameter integer C_AXI_Light_Master_ADDR_WIDTH	= 32,
		parameter integer C_AXI_Light_Master_DATA_WIDTH	= 32,
		parameter integer C_AXI_Light_Master_TRANSACTIONS_NUM	= 4,
		
		parameter integer MEM_ADRESS_WIDTH = 32, 
		parameter integer MEM_DATA_WIDTH = 16
	)
	(
		// Users to add ports here

		// User ports ends
		// Do not modify the ports beyond this line


		// Ports of Axi Slave Bus Interface AXI_Light_Slave
		input wire  axi_light_slave_aclk,
		input wire  axi_light_slave_aresetn,
		input wire [C_AXI_Light_Slave_ADDR_WIDTH-1 : 0] axi_light_slave_awaddr,
		input wire [2 : 0] axi_light_slave_awprot,
		input wire  axi_light_slave_awvalid,
		output wire  axi_light_slave_awready,
		input wire [C_AXI_Light_Slave_DATA_WIDTH-1 : 0] axi_light_slave_wdata,
		input wire [(C_AXI_Light_Slave_DATA_WIDTH/8)-1 : 0] axi_light_slave_wstrb,
		input wire  axi_light_slave_wvalid,
		output wire  axi_light_slave_wready,
		output wire [1 : 0] axi_light_slave_bresp,
		output wire  axi_light_slave_bvalid,
		input wire  axi_light_slave_bready,
		input wire [C_AXI_Light_Slave_ADDR_WIDTH-1 : 0] axi_light_slave_araddr,
		input wire [2 : 0] axi_light_slave_arprot,
		input wire  axi_light_slave_arvalid,
		output wire  axi_light_slave_arready,
		output wire [C_AXI_Light_Slave_DATA_WIDTH-1 : 0] axi_light_slave_rdata,
		output wire [1 : 0] axi_light_slave_rresp,
		output wire  axi_light_slave_rvalid,
		input wire  axi_light_slave_rready,

		// Ports of Axi Master Bus Interface AXI_Light_Master
		input wire  axi_light_master_init_axi_txn,
		output wire  axi_light_master_txn_done,
		input wire  axi_light_master_aclk,
		input wire  axi_light_master_aresetn,
		output wire [C_AXI_Light_Master_ADDR_WIDTH-1 : 0] axi_light_master_awaddr,
		output wire [2 : 0] axi_light_master_awprot,
		output wire  axi_light_master_awvalid,
		input wire  axi_light_master_awready,
		output wire [C_AXI_Light_Master_DATA_WIDTH-1 : 0] axi_light_master_wdata,
		output wire [C_AXI_Light_Master_DATA_WIDTH/8-1 : 0] axi_light_master_wstrb,
		output wire  axi_light_master_wvalid,
		input wire  axi_light_master_wready,
		input wire [1 : 0] axi_light_master_bresp,
		input wire  axi_light_master_bvalid,
		output wire  axi_light_master_bready,
		output wire [C_AXI_Light_Master_ADDR_WIDTH-1 : 0] axi_light_master_araddr,
		output wire [2 : 0] axi_light_master_arprot,
		output wire  axi_light_master_arvalid,
		input wire  axi_light_master_arready,
		input wire [C_AXI_Light_Master_DATA_WIDTH-1 : 0] axi_light_master_rdata,
		input wire [1 : 0] axi_light_master_rresp,
		input wire  axi_light_master_rvalid,
		output wire  axi_light_master_rready,
		
        output wire [7:0] cmd,
        output wire trigger_cmd_handler,

        output wire cmd_ready,
        
        input wire[MEM_DATA_WIDTH-1:0] input_data, 
        input wire[MEM_ADRESS_WIDTH-1:0] input_address, 
        output wire transmission_active,	       
        
        output wire [MEM_DATA_WIDTH-1:0]  init_value,
        output wire [MEM_DATA_WIDTH-1:0]  test_value,
        output wire [MEM_ADRESS_WIDTH-1:0]  start_addr,
        output wire [MEM_ADRESS_WIDTH-1:0]  stop_addr, 
        
        
        // PUF config parameters
        output wire[7:0] puf_type,
        output wire[15:0] hammeringIterations,
        output wire[15:0] hammeringDistance,
        output wire ce_driven,
        
        output wire reset_out,
        
        // WriteTiming
        output wire[`TIMING_BUS_WIDTH-1:0] tWaitAfterInit,
        output wire[`TIMING_BUS_WIDTH-1:0] tWaitBetweenHammering,
        output wire[`TIMING_BUS_WIDTH-1:0] tNextRead,
        
        
        // Write Timing for initialization
        output wire[`TIMING_BUS_WIDTH-1:0] tStartDefault,
        output wire[`TIMING_BUS_WIDTH-1:0] tnextWriteDefault,    
        output wire[`TIMING_BUS_WIDTH-1:0] tACDefault,
        output wire[`TIMING_BUS_WIDTH-1:0] tASDefault,
        output wire[`TIMING_BUS_WIDTH-1:0] tAHDefault,
        output wire[`TIMING_BUS_WIDTH-1:0] tDSDefault,
        output wire[`TIMING_BUS_WIDTH-1:0] tDHDefault,
        output wire[`TIMING_BUS_WIDTH-1:0] tPWDDefault,
        
        // Write Timing for latency tests
        output wire[`TIMING_BUS_WIDTH-1:0] tNextWriteAdjusted,
        output wire[`TIMING_BUS_WIDTH-1:0] tStartAdjusted,    
        output wire[`TIMING_BUS_WIDTH-1:0] tACAdjusted,
        output wire[`TIMING_BUS_WIDTH-1:0] tASAdjusted,
        output wire[`TIMING_BUS_WIDTH-1:0] tAHAdjusted,
        output wire[`TIMING_BUS_WIDTH-1:0] tDSAdjusted,
        output wire[`TIMING_BUS_WIDTH-1:0] tDHAdjusted,
        output wire[`TIMING_BUS_WIDTH-1:0] tPWDAdjusted,

		// Read Timing 
		output wire ceDrivenRead,
		output wire[`TIMING_BUS_WIDTH-1:0] tStartReadDefault,
		output wire[`TIMING_BUS_WIDTH-1:0] tasReadDefault,
		output wire[`TIMING_BUS_WIDTH-1:0] tahReadDefault,
		output wire[`TIMING_BUS_WIDTH-1:0] toedDefault,
		output wire[`TIMING_BUS_WIDTH-1:0] tprcDefault,
		output wire[`TIMING_BUS_WIDTH-1:0] tceoeEnableDefault,
		output wire[`TIMING_BUS_WIDTH-1:0] tceoeDisableDefault,

		output wire[`TIMING_BUS_WIDTH-1:0] tStartReadAdjusted,
		output wire[`TIMING_BUS_WIDTH-1:0] tasReadAdjusted,
		output wire[`TIMING_BUS_WIDTH-1:0] tahReadAdjusted,
		output wire[`TIMING_BUS_WIDTH-1:0] toedAdjusted,
		output wire[`TIMING_BUS_WIDTH-1:0] tprcAdjusted,
		output wire[`TIMING_BUS_WIDTH-1:0] tceoeEnableAdjusted,
		output wire[`TIMING_BUS_WIDTH-1:0] tceoeDisableAdjusted
       
       // FOR debug purposes
`ifdef DEBUG        
        ,output wire [(C_AXI_Light_Slave_DATA_WIDTH * C_AXI_Light_Slave_ADDR_WIDTH)-1:0] full_frame
`endif        
	);
	
	// TODO may be removed!
	wire[1:0] master_state_machine;
	wire axi_light_master_error;
    wire activate_axi_master;
    wire[1:0] write_index_out;

	wire cmdhandler_ready;
	wire [(C_AXI_Light_Slave_DATA_WIDTH * C_AXI_Light_Slave_ADDR_WIDTH)-1:0] received_data;
    assign full_frame = received_data;
	assign cmd_ready = cmdhandler_ready;
	
// Instantiation of Axi Bus Interface AXI_Light_Slave
	ps_pl_interface_v1_0_AXI_Light_Slave # ( 
		.C_S_AXI_DATA_WIDTH(C_AXI_Light_Slave_DATA_WIDTH),
		.C_S_AXI_ADDR_WIDTH(C_AXI_Light_Slave_ADDR_WIDTH)
	) axi_slave_inst (
		.S_AXI_ACLK(axi_light_slave_aclk),
		.cmd_parser_done(cmdhandler_ready),
		.S_AXI_ARESETN(axi_light_slave_aresetn),
		.S_AXI_AWADDR(axi_light_slave_awaddr),
		.S_AXI_AWPROT(axi_light_slave_awprot),
		.S_AXI_AWVALID(axi_light_slave_awvalid),
		.S_AXI_AWREADY(axi_light_slave_awready),
		.S_AXI_WDATA(axi_light_slave_wdata),
		.S_AXI_WSTRB(axi_light_slave_wstrb),
		.S_AXI_WVALID(axi_light_slave_wvalid),
		.S_AXI_WREADY(axi_light_slave_wready),
		.S_AXI_BRESP(axi_light_slave_bresp),
		.S_AXI_BVALID(axi_light_slave_bvalid),
		.S_AXI_BREADY(axi_light_slave_bready),
		.S_AXI_ARADDR(axi_light_slave_araddr),
		.S_AXI_ARPROT(axi_light_slave_arprot),
		.S_AXI_ARVALID(axi_light_slave_arvalid),
		.S_AXI_ARREADY(axi_light_slave_arready),
		.S_AXI_RDATA(axi_light_slave_rdata),
		.S_AXI_RRESP(axi_light_slave_rresp),
		.S_AXI_RVALID(axi_light_slave_rvalid),
		.S_AXI_RREADY(axi_light_slave_rready),
        .received_data(received_data),
		.write_map(write_map),
		.read_map(read_map)
	);



reg activate_axi_master_reg = 0;
wire [7:0] output_state;
    

always @ (posedge cmdhandler_ready) begin
    activate_axi_master_reg <= 1; 
end


assign activate_axi_master = activate_axi_master_reg; 


// Instantiation of Axi Bus Interface AXI_Light_Master
	ps_pl_interface_v1_0_AXI_Light_Master # ( 
		.C_M_TARGET_SLAVE_BASE_ADDR(C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR),
		.C_M_AXI_ADDR_WIDTH(C_AXI_Light_Master_ADDR_WIDTH),
		.C_M_AXI_DATA_WIDTH(C_AXI_Light_Master_DATA_WIDTH),
		.C_M_TRANSACTIONS_NUM(C_AXI_Light_Master_TRANSACTIONS_NUM)
	) axi_master_inst (
		.INIT_AXI_TXN(axi_light_master_init_axi_txn || trigger_cmd_handler),
		.ERROR(axi_light_master_error),
		.TXN_DONE(axi_light_master_txn_done),
		.M_AXI_ACLK(axi_light_master_aclk),
		.M_AXI_ARESETN(axi_light_master_aresetn),
		.M_AXI_AWADDR(axi_light_master_awaddr),
		.M_AXI_AWPROT(axi_light_master_awprot),
		.M_AXI_AWVALID(axi_light_master_awvalid),
		.M_AXI_AWREADY(axi_light_master_awready),
		.M_AXI_WDATA(axi_light_master_wdata),
		.M_AXI_WSTRB(axi_light_master_wstrb),
		.M_AXI_WVALID(axi_light_master_wvalid),
		.M_AXI_WREADY(axi_light_master_wready),
		.M_AXI_BRESP(axi_light_master_bresp),
		.M_AXI_BVALID(axi_light_master_bvalid),
		.M_AXI_BREADY(axi_light_master_bready),
		.M_AXI_ARADDR(axi_light_master_araddr),
		.M_AXI_ARPROT(axi_light_master_arprot),
		.M_AXI_ARVALID(axi_light_master_arvalid),
		.M_AXI_ARREADY(axi_light_master_arready),
		.M_AXI_RDATA(axi_light_master_rdata),
		.M_AXI_RRESP(axi_light_master_rresp),
		.M_AXI_RVALID(axi_light_master_rvalid),
		.M_AXI_RREADY(axi_light_master_rready),
		.master_state_machine(master_state_machine),
		.input_address(input_address), 
		.input_data(input_data),
		.write_index_out(write_index_out),
		.activate_axi_master(activate_axi_master_reg),
        .cmd_handler_state(output_state),
        .cmd_handler_cmd(cmd)
	);

	// Add user logic here
	wire [C_AXI_Light_Slave_DATA_WIDTH-1:0]	slv_reg1;
	wire [C_AXI_Light_Slave_DATA_WIDTH-1:0]	slv_reg2;
	wire [C_AXI_Light_Slave_DATA_WIDTH-1:0]	slv_reg3;
	
	wire[3:0] read_map;
	wire[C_AXI_Light_Slave_ADDR_WIDTH-1:0] write_map;
	
	
	
    command_handler #(.C_AXI_Light_Slave_DATA_WIDTH(32), .BUFF_LEN(C_AXI_Light_Slave_ADDR_WIDTH)) command_handler_inst 
        (.clk(axi_light_slave_aclk),
        .received_data(received_data),
        .write_map(write_map),
		.cmd(cmd),
        .init_value(init_value),
        .puf_value(test_value),
        .start_addr(start_addr),
        .stop_addr(stop_addr), 
        .read_map(read_map),
        .cmd_ready(cmdhandler_ready),
		.puf_type(puf_type),
    	.ce_driven(ce_driven),
    	.reset_out(reset_out),

    	.tWaitAfterInit(tWaitAfterInit),
    	.tNextRead(tNextRead),
    	.tStartDefault(tStartDefault),
    	.tnextWriteDefault(tnextWriteDefault),
    	.tACDefault(tACDefault),
    	.tASDefault(tASDefault),
    	.tAHDefault(tAHDefault),
    	.tPWDDefault(tPWDDefault),
    	.tDSDefault(tDSDefault),
    	.tDHDefault(tDHDefault), 
    	
    	 .tNextWriteAdjusted(tNextWriteAdjusted),
         .tStartAdjusted(tStartAdjusted),
         .tACAdjusted(tACAdjusted),
         .tASAdjusted(tASAdjusted),
         .tAHAdjusted(tAHAdjusted),
         .tDSAdjusted(tDSAdjusted),
         .tDHAdjusted(tDHAdjusted),
         .tPWDAdjusted(tPWDAdjusted),
         .trigger_cmd_handler(trigger_cmd_handler),
         .output_state(output_state),


		// Read Timing 
		.ceDrivenRead(ceDrivenRead),
		.tStartReadDefault(tStartReadDefault),
		.tasReadDefault(tasReadDefault),
		.tahReadDefault(tahReadDefault),
		.toedDefault(toedDefault),
		.tprcDefault(tprcDefault),
		.tceoeEnableDefault(tceoeEnableDefault),
		.tceoeDisableDefault(tceoeDisableDefault),

		.tStartReadAdjusted(tStartReadAdjusted),
		.tasReadAdjusted(tasReadAdjusted),
		.tahReadAdjusted(tahReadAdjusted),
		.toedAdjusted(toedAdjusted),
		.tprcAdjusted(tprcAdjusted),
		.tceoeEnableAdjusted(tceoeEnableAdjusted),
		.tceoeDisableAdjusted(tceoeDisableAdjusted),
    	
    	// Row hammering
        .hammeringIterations(hammeringIterations),
        .hammeringDistance(hammeringDistance),
        .tWaitBetweenHammering(tWaitBetweenHammering)
		);
	
	// User logic ends

	endmodule
	