// Original DE2 (EP2C35F672C6), onboard MAX232 RS-232 connector.
module de2_temperature(input CLOCK_50, input KEY0_N, input UART_RXD, output UART_TXD);
 de2_temp_predictor_top #(.COEF_FILE("coeffs.txt")) system_inst(
 .CLOCK_50(CLOCK_50),.KEY0_N(KEY0_N),.UART_RXD(UART_RXD),.UART_TXD(UART_TXD),
 .LEDR(),.HEX0(),.HEX1(),.HEX2(),.HEX3());
endmodule
