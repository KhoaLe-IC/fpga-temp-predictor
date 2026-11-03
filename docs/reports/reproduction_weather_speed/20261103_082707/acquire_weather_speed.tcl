package require ::quartus::stp
set args $quartus(args)
if {[llength $args] != 1} {
    error "Usage: acquire_weather_speed.tcl /full/path/to/weather_speed_live.stp"
}
set capture_file [file normalize [lindex $args 0]]
open_session -name $capture_file
puts "CAPTURE ARMED: send the weather_speed replay from the second terminal now"
flush stdout
run -instance auto_signaltap_0 \
    -signal_set signal_set_1 \
    -trigger trigger_1 \
    -data_log live_capture \
    -timeout 120
close_session
puts "CAPTURE SAVED: $capture_file"
