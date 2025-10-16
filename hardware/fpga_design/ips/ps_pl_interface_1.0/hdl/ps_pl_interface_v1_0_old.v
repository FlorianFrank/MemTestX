
`timescale 1 ns / 1 ps

	module ps_pl_interface_v1_0 #
	(
		// Users to add parameters here

		// User parameters ends
		// Do not modify the parameters beyond this line


		// Parameters of Axi Slave Bus Interface AXI_Light_Slave
		parameter integer C_AXI_Light_Slave_DATA_WIDTH	= 32,
		parameter integer C_AXI_Light_Slave_ADDR_WIDTH	= 4,

		// Parameters of Axi Master Bus Interface AXI_Light_Master
		parameter  C_AXI_Light_Master_START_DATA_VALUE	= 32'hAA000000,
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
		output wire  axi_light_master_error,
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
		
		output wire [7:0]   measure_type,
        output wire [MEM_DATA_WIDTH-1:0]  init_value,
        output wire [MEM_ADRESS_WIDTH-1:0]  start_addr,
        output wire [MEM_ADRESS_WIDTH-1:0]  stop_addr, 
        output wire [32:0]  time_value,
        output wire [127:0] auxilary_data,
        output wire [7:0] cmd,
        output wire [10:0] buffer_ctr_tmp,
        
        output wire [3:0] read_map_out, 
        output wire [3:0] write_map_out,
        output wire cmd_ready,
        
        input wire[MEM_DATA_WIDTH-1:0] input_data, 
        input wire[MEM_ADRESS_WIDTH-1:0] input_address, 
        output wire transmission_active,
		
        output wire[1:0] master_state_machine,
        output wire[1:0] write_index_out
	);


	wire [C_AXI_Light_Slave_DATA_WIDTH-1:0]	slv_reg0;
	wire [C_AXI_Light_Slave_DATA_WIDTH-1:0]	slv_reg1;
	wire [C_AXI_Light_Slave_DATA_WIDTH-1:0]	slv_reg2;
	wire [C_AXI_Light_Slave_DATA_WIDTH-1:0]	slv_reg3;
	
	wire[3:0] read_map;
	wire[3:0] write_map;
	
	wire cmd_ready;
	
	
    command_handler #(.C_AXI_Light_Slave_DATA_WIDTH(32), .BUFF_LEN(12)) command_handler_inst 
        (.clk(axi_light_slave_aclk),
        .slv_reg0(slv_reg0),
        .slv_reg1(slv_reg1),
        .slv_reg2(slv_reg2),
        .slv_reg3(slv_reg3),
        .write_map(write_map),
        		
		.measure_type(measure_type),
		.buffer_ctr_tmp(buffer_ctr_tmp),
		.cmd(cmd),
        .init_value(init_value),
        .start_addr(start_addr),
        .stop_addr(stop_addr), 
        .time_value(time_value),
        .auxilary_data(auxilary_data),
        .read_map(read_map),
        .cmd_ready(cmd_ready));
	

	assign read_map_out = read_map;
	assign write_map_out = write_map;
	
// Instantiation of Axi Bus Interface AXI_Light_Slave
	ps_pl_interface_v1_0_AXI_Light_Slave # ( 
		.C_S_AXI_DATA_WIDTH(C_AXI_Light_Slave_DATA_WIDTH),
		.C_S_AXI_ADDR_WIDTH(C_AXI_Light_Slave_ADDR_WIDTH)
	) ps_pl_interface_v1_0_AXI_Light_Slave_inst (
		.S_AXI_ACLK(axi_light_slave_aclk),
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
		.slv_reg0(slv_reg0),
		.slv_reg1(slv_reg1),
		.slv_reg2(slv_reg2),
		.slv_reg3(slv_reg3),
		.write_map(write_map),
		.read_map(read_map)
	);


// Instantiation of Axi Bus Interface AXI_Light_Master
	ps_pl_interface_v1_0_AXI_Light_Master # ( 
		.C_M_START_DATA_VALUE(C_AXI_Light_Master_START_DATA_VALUE),
		.C_M_TARGET_SLAVE_BASE_ADDR(C_AXI_Light_Master_TARGET_SLAVE_BASE_ADDR),
		.C_M_AXI_ADDR_WIDTH(C_AXI_Light_Master_ADDR_WIDTH),
		.C_M_AXI_DATA_WIDTH(C_AXI_Light_Master_DATA_WIDTH),
		.C_M_TRANSACTIONS_NUM(C_AXI_Light_Master_TRANSACTIONS_NUM)
	) ps_pl_interface_v1_0_AXI_Light_Master_inst (
		.INIT_AXI_TXN(axi_light_master_init_axi_txn),
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
		.write_index_out(write_index_out)
	);

	// Add user logic here
	
	
		reg[2:0] cur, next;
		
		reg axi_txn = 0;

		parameter t_0=3'b000; 
		parameter t_1=3'b001; 
		parameter t_2=3'b010;
		parameter t_3=3'b011; 
		parameter t_4=3'b100; 
		parameter t_5=3'b101; 
		parameter t_6=3'b110;
	
	
always @(posedge axi_light_master_aclk) begin
		if(axi_light_master_aresetn==1'b0) begin
			cur<=t_0;
		end
		else begin
			cur<=next;
		end
	end




	//state calculation
	always @(*) begin
		case(cur) 
			t_0: begin
				if(axi_txn) next=t_1;
				else next=t_0;
			end
			t_1: begin
				next=t_2;
			end
			t_2: begin
				if(axi_light_master_awready) begin
					if(axi_light_master_wready) next=t_4;
					else next=t_3;
				end
				else next=t_2;
			end
			t_3: begin
				if(axi_light_master_wready) next=t_4;
				else next=t_3;
			end
			t_4: begin
				if(axi_light_master_awready) begin
					if(axi_light_master_wready) next=t_6;
					else next=t_5;
				end
				else next=t_4;
			end
			t_5: begin
				if(axi_light_master_wready) next=t_6;
				else next=t_5;
			end
			t_6: begin
				next=t_6;
			end
		default  next=t_0;
		endcase
	end    
	
	    
	// User logic ends

	endmodule
	