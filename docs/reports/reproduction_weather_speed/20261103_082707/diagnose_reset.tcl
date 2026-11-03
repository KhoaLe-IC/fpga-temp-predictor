package require ::quartus::insystem_source_probe
set hw [lindex [get_hardware_names] 0]
set dev [lindex [get_device_names -hardware_name $hw] 0]
start_insystem_source_probe -hardware_name $hw -device_name $dev
foreach value {2 0} {
 write_source_data -instance_index 0 -value $value -value_in_hex
 after 100
 for {set i 0} {$i<3} {incr i} {
 set h [read_probe_data -instance_index 0 -value_in_hex]
 set p [expr 0x$h]
 puts "source=$value probe=$h reset_active=[expr {($p>>165)&1}] ready=[expr {($p>>164)&1}] ack=[expr {($p>>160)&1}]"
 after 100
 }
}
end_insystem_source_probe
