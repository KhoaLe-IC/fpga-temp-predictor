package require ::quartus::insystem_source_probe
set hw [lindex [get_hardware_names] 0]
set dev [lindex [get_device_names -hardware_name $hw] 0]
puts "Hardware: $hw; Device: $dev"
puts "Node: [get_insystem_source_probe_instance_info -hardware_name $hw -device_name $dev]"
start_insystem_source_probe -hardware_name $hw -device_name $dev
set h [read_probe_data -instance_index 0 -value_in_hex]
set p [expr 0x$h]
puts "Probe: $h"
puts "Accepted=[expr {($p>>128)&65535}] Forecasts=[expr {($p>>144)&65535}] Reset=[expr {($p>>165)&1}]"
end_insystem_source_probe
