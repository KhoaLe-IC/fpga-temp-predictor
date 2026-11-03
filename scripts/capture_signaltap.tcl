# Real SignalTap acquisition; stimulus runs separately through the JTAG mailbox.
package require ::quartus::stp
set root [file normalize [file join [file dirname [info script]] ..]]
set variant [lindex $argv 0]
if {$variant ni {temperature_speed temperature_resource weather_speed weather_resource}} {error "invalid variant"}
set dest [file join $root docs reports defense_session signaltap]
file mkdir $dest
set capture [file join $dest ${variant}.stp]
file copy -force [file join $root hardware quartus signaltap $variant capture.stp] $capture
open_session -name $capture
run -instance auto_signaltap_0 -signal_set signal_set_1 -trigger trigger_1 -data_log physical_capture -timeout 30
close_session
puts "SIGNALTAP SESSION CLOSED $variant: $capture"
